from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from .database import DatabaseSchema
from .types import GeneratedQuery, QueryPlan


class LLMGenerationError(RuntimeError):
    """Raised when LLM-based SQL generation fails."""


class SQLLLMClient(Protocol):
    def generate(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> GeneratedQuery:
        """Generate SQL from natural language prompt context."""


@dataclass(frozen=True)
class OpenAIChatCompletionsClient:
    api_key: str
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 30.0

    def generate(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> GeneratedQuery:
        try:
            import httpx
        except ModuleNotFoundError as exc:  # pragma: no cover - env dependent
            raise LLMGenerationError(
                "httpx is required for OpenAI integration. Install project dependencies."
            ) from exc

        system_prompt = (
            "You are a SQL generation assistant for SQLite. "
            "Generate a single read-only SQL query. "
            "Always return strict JSON with keys: sql, selected_table, reasoning."
        )
        user_prompt = self._build_user_prompt(question=question, plan=plan, schema=schema)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        url = f"{self.base_url.rstrip('/')}/chat/completions"

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
            message = body["choices"][0]["message"]["content"]
            parsed = self._parse_json_payload(message)
            return GeneratedQuery(
                sql=parsed["sql"],
                selected_table=parsed["selected_table"],
                reasoning=parsed["reasoning"],
            )
        except Exception as exc:  # pragma: no cover - network dependent
            raise LLMGenerationError(f"OpenAI generation failed: {exc}") from exc

    def _build_user_prompt(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> str:
        schema_lines = []
        for table, columns in schema.tables.items():
            schema_lines.append(f'- {table}: {", ".join(columns)}')
        schema_text = "\n".join(schema_lines)
        notes = "; ".join(plan.notes) if plan.notes else "none"

        return (
            f"Question: {question}\n"
            f"Intent: {plan.intent}\n"
            f"Table hint: {plan.table_hint or 'none'}\n"
            f"Limit: {plan.limit}\n"
            f"Planning notes: {notes}\n\n"
            f"Database schema:\n{schema_text}\n\n"
            "Rules:\n"
            "1) Use only tables and columns from schema.\n"
            "2) Output read-only SQL only (SELECT/WITH).\n"
            "3) Prefer deterministic ordering for top/list queries.\n"
            "4) Include LIMIT when returning rows.\n"
            "5) Return strict JSON with keys sql, selected_table, reasoning."
        )

    def _parse_json_payload(self, content: str) -> dict[str, str]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMGenerationError("LLM response was not valid JSON.") from exc

        required = ("sql", "selected_table", "reasoning")
        missing = [key for key in required if key not in data]
        if missing:
            raise LLMGenerationError(f"LLM response missing keys: {', '.join(missing)}")

        if not all(isinstance(data[key], str) and data[key].strip() for key in required):
            raise LLMGenerationError("LLM response keys must be non-empty strings.")

        return {
            "sql": data["sql"].strip(),
            "selected_table": data["selected_table"].strip(),
            "reasoning": data["reasoning"].strip(),
        }
