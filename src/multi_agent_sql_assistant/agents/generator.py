from __future__ import annotations

import re

from ..database import DatabaseSchema
from ..llm import LLMGenerationError, SQLLLMClient
from ..types import GeneratedQuery, QueryPlan


class SQLGeneratorAgent:
    def __init__(self, llm_client: SQLLLMClient | None = None) -> None:
        self.llm_client = llm_client

    def generate(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> GeneratedQuery:
        if not schema.tables:
            raise ValueError("Database has no queryable tables.")

        if self.llm_client is not None:
            try:
                llm_query = self.llm_client.generate(question=question, plan=plan, schema=schema)
                normalized = self._normalize_llm_query(llm_query, schema=schema)
                return GeneratedQuery(
                    sql=normalized.sql,
                    selected_table=normalized.selected_table,
                    reasoning=f"llm generation -> {normalized.reasoning}",
                )
            except (LLMGenerationError, ValueError):
                # Silent fallback to deterministic heuristic generation.
                pass

        return self._heuristic_generate(question=question, plan=plan, schema=schema)

    def _heuristic_generate(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> GeneratedQuery:
        table = self._select_table(question=question, plan=plan, schema=schema)
        columns = schema.tables[table]

        if plan.intent == "count":
            sql = f'SELECT COUNT(*) AS total_count FROM "{table}"'
            reasoning = "count intent -> aggregate row count"
        elif plan.intent == "top":
            sort_column = self._choose_sort_column(columns)
            sql = (
                f'SELECT * FROM "{table}" '
                f'ORDER BY "{sort_column}" DESC '
                f'LIMIT {plan.limit}'
            )
            reasoning = f"top intent -> sort by {sort_column}"
        else:
            sql = f'SELECT * FROM "{table}" LIMIT {plan.limit}'
            reasoning = "list intent -> preview records"

        return GeneratedQuery(sql=sql, selected_table=table, reasoning=reasoning)

    def _normalize_llm_query(self, query: GeneratedQuery, schema: DatabaseSchema) -> GeneratedQuery:
        if not query.sql.strip():
            raise ValueError("LLM returned empty SQL.")
        lowered = query.sql.lower().strip()
        if not (lowered.startswith("select") or lowered.startswith("with")):
            raise ValueError("LLM returned non-read SQL prefix.")

        selected_table = query.selected_table
        if selected_table not in schema.tables:
            extracted = re.findall(
                r'\b(?:from|join)\s+["`]?([a-zA-Z_][\w]*)',
                query.sql,
                flags=re.IGNORECASE,
            )
            matched = next((item for item in extracted if item in schema.tables), None)
            if not matched:
                raise ValueError("LLM selected table is not in schema.")
            selected_table = matched

        return GeneratedQuery(
            sql=query.sql.strip().rstrip(";"),
            selected_table=selected_table,
            reasoning=query.reasoning,
        )

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
