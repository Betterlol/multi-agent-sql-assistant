from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

from .agents.generator import SQLGeneratorAgent
from .agents.verifier import SQLVerificationError
from .database import SQLiteDatabaseClient
from .llm import OpenAIChatCompletionsClient, SQLLLMClient
from .pipeline import SQLAssistantPipeline
from .settings import load_settings

MAX_UPLOAD_BYTES = 30 * 1024 * 1024
UPLOAD_REGISTRY: dict[str, Path] = {}


class LLMConfig(BaseModel):
    enabled: bool = False
    provider: str = "openai"
    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None

    @model_validator(mode="after")
    def normalize_fields(self) -> "LLMConfig":
        self.provider = self.provider.strip().lower()
        if self.api_key is not None:
            self.api_key = self.api_key.strip() or None
        if self.model is not None:
            self.model = self.model.strip() or None
        if self.base_url is not None:
            self.base_url = self.base_url.strip() or None
        return self


class QueryRequest(BaseModel):
    database_path: str | None = Field(default=None, description="SQLite database file path")
    database_id: str | None = Field(default=None, description="Database id from /v1/upload-db")
    question: str = Field(..., min_length=1)
    max_rows: int = Field(100, ge=1, le=1000)
    llm: LLMConfig | None = Field(default=None, description="Optional per-request LLM config")

    @model_validator(mode="after")
    def validate_database_source(self) -> "QueryRequest":
        has_path = bool(self.database_path and self.database_path.strip())
        has_id = bool(self.database_id and self.database_id.strip())
        if has_path == has_id:
            raise ValueError("Provide exactly one of database_path or database_id.")

        if self.database_path is not None:
            self.database_path = self.database_path.strip()
        if self.database_id is not None:
            self.database_id = self.database_id.strip()
        return self


class QueryResponse(BaseModel):
    plan_intent: str
    selected_table: str
    generated_sql: str
    verified_sql: str
    warnings: list[str]
    columns: list[str]
    rows: list[list[object]]
    row_count: int


class UploadDatabaseResponse(BaseModel):
    database_id: str
    filename: str
    table_names: list[str]
    table_count: int


def _build_llm_client() -> SQLLLMClient | None:
    settings = load_settings()
    if settings.llm_provider != "openai":
        return None
    if not settings.openai_api_key:
        return None

    return OpenAIChatCompletionsClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        base_url=settings.openai_base_url,
    )


default_pipeline = SQLAssistantPipeline(generator=SQLGeneratorAgent(llm_client=_build_llm_client()))


def _build_request_llm_client(llm_config: LLMConfig | None) -> SQLLLMClient | None:
    if llm_config is None or not llm_config.enabled:
        return None

    if llm_config.provider != "openai":
        raise HTTPException(status_code=400, detail=f"Unsupported LLM provider: {llm_config.provider}")

    settings = load_settings()
    api_key = llm_config.api_key or settings.openai_api_key
    if not api_key:
        raise HTTPException(status_code=400, detail="LLM is enabled but API key is missing.")

    return OpenAIChatCompletionsClient(
        api_key=api_key,
        model=llm_config.model or settings.openai_model,
        base_url=llm_config.base_url or settings.openai_base_url,
    )


def _resolve_database_path(request: QueryRequest) -> str:
    if request.database_path:
        return request.database_path

    assert request.database_id is not None
    resolved = UPLOAD_REGISTRY.get(request.database_id)
    if resolved is None:
        raise HTTPException(
            status_code=404,
            detail="Uploaded database not found. Please upload file again.",
        )
    return str(resolved)


def create_app() -> FastAPI:
    app = FastAPI(title="Multi-Agent SQL Assistant", version="0.1.0")
    web_root = Path(__file__).resolve().parent / "web"
    upload_root = Path.cwd() / "runtime_uploads"
    upload_root.mkdir(parents=True, exist_ok=True)

    app.mount("/static", StaticFiles(directory=web_root), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(web_root / "index.html")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/upload-db", response_model=UploadDatabaseResponse)
    async def upload_db(file: UploadFile = File(...)) -> UploadDatabaseResponse:
        filename = file.filename or "uploaded.sqlite"
        suffix = Path(filename).suffix.lower()
        if suffix not in {".sqlite", ".sqlite3", ".db"}:
            raise HTTPException(
                status_code=400,
                detail="Only SQLite files are supported (.sqlite, .sqlite3, .db).",
            )

        payload = await file.read(MAX_UPLOAD_BYTES + 1)
        await file.close()
        if len(payload) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=400, detail=f"File is too large. Max {MAX_UPLOAD_BYTES} bytes.")

        database_id = uuid4().hex
        stored_path = upload_root / f"{database_id}.sqlite"
        stored_path.write_bytes(payload)

        try:
            db_client = SQLiteDatabaseClient(str(stored_path))
            schema = db_client.inspect_schema()
        except Exception as exc:
            stored_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail=f"Invalid SQLite file: {exc}") from exc

        if not schema.tables:
            stored_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Uploaded database has no queryable tables.")

        UPLOAD_REGISTRY[database_id] = stored_path
        return UploadDatabaseResponse(
            database_id=database_id,
            filename=filename,
            table_names=sorted(schema.tables.keys()),
            table_count=len(schema.tables),
        )

    @app.post("/v1/query", response_model=QueryResponse)
    def query_sql(request: QueryRequest) -> QueryResponse:
        try:
            database_path = _resolve_database_path(request)
            db_client = SQLiteDatabaseClient(database_path)
            schema = db_client.inspect_schema()
            if not schema.tables:
                raise HTTPException(status_code=400, detail="Database has no queryable tables.")

            request_llm_client = _build_request_llm_client(request.llm)
            pipeline = (
                SQLAssistantPipeline(generator=SQLGeneratorAgent(llm_client=request_llm_client))
                if request_llm_client is not None
                else default_pipeline
            )

            pipeline_result = pipeline.run(
                question=request.question,
                schema=schema,
                max_rows=request.max_rows,
            )
            query_result = db_client.execute_query(
                pipeline_result.verified_query.sql,
                max_rows=request.max_rows,
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except SQLVerificationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover - defensive fallback for API
            raise HTTPException(status_code=500, detail=f"Internal error: {exc}") from exc

        return QueryResponse(
            plan_intent=pipeline_result.plan.intent,
            selected_table=pipeline_result.generated_query.selected_table,
            generated_sql=pipeline_result.generated_query.sql,
            verified_sql=pipeline_result.verified_query.sql,
            warnings=pipeline_result.verified_query.warnings,
            columns=query_result.columns,
            rows=query_result.rows,
            row_count=query_result.row_count,
        )

    return app
