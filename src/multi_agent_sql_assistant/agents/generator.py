from __future__ import annotations

import re

from ..database import DatabaseSchema
from ..types import GeneratedQuery, QueryPlan


class SQLGeneratorAgent:
    def generate(self, question: str, plan: QueryPlan, schema: DatabaseSchema) -> GeneratedQuery:
        if not schema.tables:
            raise ValueError("Database has no queryable tables.")

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
