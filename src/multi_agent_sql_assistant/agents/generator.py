from __future__ import annotations

import re

from ..database import DatabaseSchema
from ..llm import LLMGenerationError, SQLSpecLLMClient
from ..types import GeneratedQuery, QueryPlan, QuerySort, QuerySpec
from .spec_verifier import QuerySpecVerifier
from .sql_builder import SQLBuilder


class SQLGeneratorAgent:
    def __init__(self, llm_client: SQLSpecLLMClient | None = None) -> None:
        self.llm_client = llm_client

    def generate_spec(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> QuerySpec:
        if not schema.tables:
            raise ValueError("Database has no queryable tables.")

        generate_spec = getattr(self.llm_client, "generate_spec", None) if self.llm_client is not None else None
        if callable(generate_spec):
            try:
                llm_spec = generate_spec(question=question, plan=plan, schema=schema)
                normalized = self._normalize_llm_spec(llm_spec, plan=plan, schema=schema)
                reasoning = normalized.reasoning or "no reasoning"
                return QuerySpec(
                    target_table=normalized.target_table,
                    select=normalized.select,
                    filters=normalized.filters,
                    search=normalized.search,
                    sort=normalized.sort,
                    limit=normalized.limit,
                    offset=normalized.offset,
                    mode=normalized.mode,
                    reasoning=f"llm spec generation -> {reasoning}",
                )
            except (LLMGenerationError, TypeError, ValueError):
                # Silent fallback to deterministic heuristic generation.
                pass

        return self._heuristic_generate_spec(question=question, plan=plan, schema=schema)

    def generate(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> GeneratedQuery:
        spec = self.generate_spec(question=question, plan=plan, schema=schema)
        verified_spec = QuerySpecVerifier().verify(spec=spec, schema=schema, max_limit=max(plan.limit, 1))
        return SQLBuilder().build(verified_spec)

    def _heuristic_generate_spec(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> QuerySpec:
        table = self._select_table(question=question, plan=plan, schema=schema)
        columns = schema.tables[table]

        mode = "count" if plan.intent == "count" else "list"
        sort: list[QuerySort] = []

        if plan.intent == "top":
            sort_column = self._choose_sort_column(columns)
            sort = [QuerySort(field=sort_column, direction="desc")]
            reasoning = f"heuristic spec generation -> top intent sorted by {sort_column}"
        elif plan.intent == "count":
            reasoning = "heuristic spec generation -> count intent"
        else:
            reasoning = "heuristic spec generation -> list intent"

        return QuerySpec(
            target_table=table,
            select=["*"],
            filters=[],
            search=None,
            sort=sort,
            limit=plan.limit,
            offset=0,
            mode=mode,
            reasoning=reasoning,
        )

    def _normalize_llm_spec(self, spec: QuerySpec, plan: QueryPlan, schema: DatabaseSchema) -> QuerySpec:
        if not isinstance(spec, QuerySpec):
            raise ValueError("LLM must return QuerySpec.")

        target_table = spec.target_table.strip()
        if not target_table:
            raise ValueError("LLM QuerySpec missing target_table.")

        table_lookup = {name.lower(): name for name in schema.tables}
        matched_table = table_lookup.get(target_table.lower())
        if matched_table is None:
            raise ValueError("LLM target_table not found in schema.")

        normalized_select = spec.select or ["*"]
        normalized_limit = self._coerce_int(spec.limit, default=plan.limit)
        if normalized_limit < 1:
            normalized_limit = plan.limit

        normalized_offset = self._coerce_int(spec.offset, default=0)
        if normalized_offset < 0:
            normalized_offset = 0

        default_mode = "count" if plan.intent == "count" else "list"
        normalized_mode = (spec.mode or default_mode).strip().lower()

        normalized_sort = [QuerySort(field=item.field, direction=(item.direction or "asc").lower()) for item in spec.sort]

        return QuerySpec(
            target_table=matched_table,
            select=normalized_select,
            filters=spec.filters,
            search=spec.search,
            sort=normalized_sort,
            limit=normalized_limit,
            offset=normalized_offset,
            mode=normalized_mode,
            reasoning=spec.reasoning,
        )

    def _coerce_int(self, value: object, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _select_table(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> str:
        lowered = question.lower()
        if plan.table_hint:
            for table in schema.tables:
                if table.lower() == plan.table_hint.lower():
                    return table

        word_tokens = set(re.findall(r"[a-zA-Z_][\w]*", lowered))
        best_table = None
        best_score = -1

        for table, cols in schema.tables.items():
            score = 0
            table_tokens = {table.lower(), table.lower().rstrip("s")}
            if table.lower() in word_tokens or table.lower().rstrip("s") in word_tokens:
                score += 3
            if table_tokens & word_tokens:
                score += 1

            for col in cols:
                col_l = col.lower()
                if col_l in word_tokens:
                    score += 1

            if score > best_score:
                best_score = score
                best_table = table

        assert best_table is not None
        return best_table

    def _choose_sort_column(self, columns: list[str]) -> str:
        preferred_patterns = ("amount", "price", "total", "score", "count", "qty", "quantity")
        for column in columns:
            lower = column.lower()
            if any(keyword in lower for keyword in preferred_patterns):
                return column

        for column in columns:
            if column.lower() not in {"id", "created_at", "updated_at"}:
                return column

        return columns[0]
