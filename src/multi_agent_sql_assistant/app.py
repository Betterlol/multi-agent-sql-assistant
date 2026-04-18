from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .agents.verifier import SQLVerificationError
from .database import SQLiteDatabaseClient
from .pipeline import SQLAssistantPipeline


class QueryRequest(BaseModel):
    database_path: str = Field(..., description="SQLite database file path")
    question: str = Field(..., min_length=1)
    max_rows: int = Field(100, ge=1, le=1000)


class QueryResponse(BaseModel):
    plan_intent: str
    selected_table: str
    generated_sql: str
    verified_sql: str
    warnings: list[str]
    columns: list[str]
    rows: list[list[object]]
    row_count: int


pipeline = SQLAssistantPipeline()


def create_app() -> FastAPI:
    app = FastAPI(title="Multi-Agent SQL Assistant", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/query", response_model=QueryResponse)
    def query_sql(request: QueryRequest) -> QueryResponse:
        try:
            db_client = SQLiteDatabaseClient(request.database_path)
            schema = db_client.inspect_schema()
            if not schema.tables:
                raise HTTPException(status_code=400, detail="Database has no queryable tables.")

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
