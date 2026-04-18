from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppSettings:
    llm_provider: str | None
    openai_api_key: str | None
    openai_model: str
    openai_base_url: str


def load_settings() -> AppSettings:
    provider = _normalize_nullable(os.getenv("SQL_ASSISTANT_LLM_PROVIDER"))
    openai_api_key = _normalize_nullable(os.getenv("OPENAI_API_KEY"))
    model = os.getenv("SQL_ASSISTANT_OPENAI_MODEL", "gpt-4o-mini").strip()
    base_url = os.getenv("SQL_ASSISTANT_OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    return AppSettings(
        llm_provider=provider,
        openai_api_key=openai_api_key,
        openai_model=model,
        openai_base_url=base_url,
    )


def _normalize_nullable(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None
