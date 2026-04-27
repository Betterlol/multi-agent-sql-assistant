from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from .database import DatabaseSchema
from .types import GeneratedQuery, QueryFilter, QueryPlan, QuerySearch, QuerySort, QuerySpec


class LLMGenerationError(RuntimeError):
    """Raised when LLM-based SQL generation fails."""


class SQLLLMClient(Protocol):
    def generate(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> GeneratedQuery:
        """Legacy protocol for direct SQL generation."""


class SQLSpecLLMClient(Protocol):
    def generate_spec(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> QuerySpec:
        """Generate query spec from natural language prompt context."""


@dataclass(frozen=True)
class OpenAIChatCompletionsClient:
    api_key: str
    model: str = "gpt-4o-mini"
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 30.0

    def generate_spec(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> QuerySpec:
        try:
            import httpx
        except ModuleNotFoundError as exc:  # pragma: no cover - env dependent
            raise LLMGenerationError(
                "httpx is required for OpenAI integration. Install project dependencies."
            ) from exc

        system_prompt = (
            "You are a query-planning assistant for SQLite. "
            "Return structured query specification JSON only. "
            "Do not output SQL. "
            "Use exactly one table."
        )
        user_prompt = self._build_spec_user_prompt(question=question, plan=plan, schema=schema)
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
            return self._coerce_query_spec(parsed, plan=plan, schema=schema)
        except Exception as exc:  # pragma: no cover - network dependent
            raise LLMGenerationError(f"OpenAI spec generation failed: {exc}") from exc

    def generate(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> GeneratedQuery:
        spec = self.generate_spec(question=question, plan=plan, schema=schema)
        sql = self._spec_to_legacy_sql(spec)
        reasoning = spec.reasoning or "no reasoning"
        return GeneratedQuery(
            sql=sql,
            selected_table=spec.target_table,
            reasoning=f"llm spec generation -> {reasoning}",
        )

    def _build_spec_user_prompt(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> str:
        schema_lines = []
        for table, columns in schema.tables.items():
            schema_lines.append(f'- {table}: {", ".join(columns)}')
        schema_text = "\n".join(schema_lines)
        notes = "; ".join(plan.notes) if plan.notes else "none"
        default_mode = "count" if plan.intent == "count" else "list"

        example = {
            "target_table": "orders",
            "select": ["*"],
            "filters": [{"field": "amount", "op": ">=", "value": 100}],
            "search": {"query": "vip", "fields": ["customer_name", "note"]},
            "sort": [{"field": "updated_at", "direction": "desc"}],
            "limit": plan.limit,
            "offset": 0,
            "mode": default_mode,
            "reasoning": "selected by intent and field relevance",
        }

        return (
            f"Question: {question}\n"
            f"Intent: {plan.intent}\n"
            f"Table hint: {plan.table_hint or 'none'}\n"
            f"Limit: {plan.limit}\n"
            f"Planning notes: {notes}\n\n"
            f"Database schema:\n{schema_text}\n\n"
            "Rules:\n"
            "1) Return strict JSON only.\n"
            "2) Do not return SQL.\n"
            "3) Use exactly one table from schema.\n"
            "4) Use existing fields only; if unsure pick most likely and explain in reasoning.\n"
            "5) mode must be list or count.\n"
            "6) Supported ops: =, !=, >, >=, <, <=, contains, not_contains, in, between, is_null, is_not_null.\n"
            f"7) JSON example: {json.dumps(example, ensure_ascii=False)}"
        )

    def _parse_json_payload(self, content: str) -> dict[str, Any]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMGenerationError("LLM response was not valid JSON.") from exc

        if not isinstance(data, dict):
            raise LLMGenerationError("LLM response root must be a JSON object.")
        return data

    def _coerce_query_spec(self, data: dict[str, Any], plan: QueryPlan, schema: DatabaseSchema) -> QuerySpec:
        if not schema.tables:
            raise LLMGenerationError("Schema has no queryable tables.")

        target_table = str(data.get("target_table") or plan.table_hint or next(iter(schema.tables))).strip()
        select = self._as_string_list(data.get("select")) or ["*"]

        filters: list[QueryFilter] = []
        raw_filters = data.get("filters")
        if isinstance(raw_filters, list):
            for item in raw_filters:
                if not isinstance(item, dict):
                    continue
                filters.append(
                    QueryFilter(
                        field=str(item.get("field") or "").strip(),
                        op=str(item.get("op") or "").strip().lower(),
                        value=item.get("value"),
                        value2=item.get("value2"),
                    )
                )

        search = None
        raw_search = data.get("search")
        if isinstance(raw_search, dict):
            search = QuerySearch(
                query=str(raw_search.get("query") or "").strip(),
                fields=self._as_string_list(raw_search.get("fields")),
            )

        sort: list[QuerySort] = []
        raw_sort = data.get("sort")
        if isinstance(raw_sort, list):
            for item in raw_sort:
                if not isinstance(item, dict):
                    continue
                sort.append(
                    QuerySort(
                        field=str(item.get("field") or "").strip(),
                        direction=str(item.get("direction") or "asc").strip().lower(),
                    )
                )

        limit = self._coerce_int(data.get("limit"), default=plan.limit)
        offset = self._coerce_int(data.get("offset"), default=0)
        mode_default = "count" if plan.intent == "count" else "list"
        mode = str(data.get("mode") or mode_default).strip().lower()
        reasoning = str(data.get("reasoning") or "").strip()

        return QuerySpec(
            target_table=target_table,
            select=select,
            filters=filters,
            search=search,
            sort=sort,
            limit=limit,
            offset=offset,
            mode=mode,
            reasoning=reasoning,
        )

    def _spec_to_legacy_sql(self, spec: QuerySpec) -> str:
        table = self._quote_ident(spec.target_table)
        if spec.mode == "count":
            return f"SELECT COUNT(*) AS total_count FROM {table}"

        if spec.select == ["*"]:
            select_clause = "*"
        else:
            select_clause = ", ".join(self._quote_ident(col) for col in spec.select)

        sql = f"SELECT {select_clause} FROM {table}"
        if spec.sort:
            order_fragments = [
                f"{self._quote_ident(item.field)} {item.direction.upper()}"
                for item in spec.sort
            ]
            sql += " ORDER BY " + ", ".join(order_fragments)
        sql += f" LIMIT {max(spec.limit, 1)}"
        if spec.offset > 0:
            sql += f" OFFSET {spec.offset}"
        return sql

    def _as_string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        items: list[str] = []
        for entry in value:
            if isinstance(entry, str) and entry.strip():
                items.append(entry.strip())
        return items

    def _coerce_int(self, value: Any, default: int) -> int:
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _quote_ident(self, name: str) -> str:
        escaped = name.replace('"', '""')
        return f'"{escaped}"'
