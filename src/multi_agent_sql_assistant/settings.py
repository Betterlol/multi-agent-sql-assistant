from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    llm_provider: str | None
    openai_api_key: str | None
    openai_model: str
    openai_base_url: str
    upload_root: Path
    upload_ttl_seconds: int
    upload_max_bytes: int
    log_level: str


def load_settings() -> AppSettings:
    provider = _normalize_nullable(os.getenv("SQL_ASSISTANT_LLM_PROVIDER"))
    openai_api_key = _normalize_nullable(os.getenv("OPENAI_API_KEY"))
    model = os.getenv("SQL_ASSISTANT_OPENAI_MODEL", "gpt-4o-mini").strip()
    base_url = os.getenv("SQL_ASSISTANT_OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    upload_root = Path(
        os.getenv(
            "SQL_ASSISTANT_UPLOAD_ROOT",
            str(Path(tempfile.gettempdir()) / "multi-agent-sql-assistant" / "runtime_uploads"),
        )
    ).resolve()
    upload_ttl_seconds = _parse_int(os.getenv("SQL_ASSISTANT_UPLOAD_TTL_SECONDS"), default=24 * 60 * 60)
    upload_max_bytes = _parse_int(os.getenv("SQL_ASSISTANT_UPLOAD_MAX_BYTES"), default=30 * 1024 * 1024)
    log_level = os.getenv("SQL_ASSISTANT_LOG_LEVEL", "INFO").strip().upper()

    return AppSettings(
        llm_provider=provider,
        openai_api_key=openai_api_key,
        openai_model=model,
        openai_base_url=base_url,
        upload_root=upload_root,
        upload_ttl_seconds=max(upload_ttl_seconds, 1),
        upload_max_bytes=max(upload_max_bytes, 1),
        log_level=log_level,
    )


def _normalize_nullable(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


def _parse_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value.strip())
    except (TypeError, ValueError):
        return default
