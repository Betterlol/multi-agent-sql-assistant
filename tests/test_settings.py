from __future__ import annotations

from multi_agent_sql_assistant.settings import load_settings


def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("SQL_ASSISTANT_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("SQL_ASSISTANT_OPENAI_MODEL", raising=False)
    monkeypatch.delenv("SQL_ASSISTANT_OPENAI_BASE_URL", raising=False)

    settings = load_settings()

    assert settings.llm_provider is None
    assert settings.openai_api_key is None
    assert settings.openai_model == "gpt-4o-mini"
    assert settings.openai_base_url == "https://api.openai.com/v1"


def test_settings_custom_env(monkeypatch) -> None:
    monkeypatch.setenv("SQL_ASSISTANT_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("SQL_ASSISTANT_OPENAI_MODEL", "gpt-4o")
    monkeypatch.setenv("SQL_ASSISTANT_OPENAI_BASE_URL", "https://example.com/v1")

    settings = load_settings()

    assert settings.llm_provider == "openai"
    assert settings.openai_api_key == "test-key"
    assert settings.openai_model == "gpt-4o"
    assert settings.openai_base_url == "https://example.com/v1"
