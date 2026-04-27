from __future__ import annotations

from ..types import BuiltQuery, QueryFilter, QuerySearch, QuerySort, VerifiedQuerySpec


class SQLBuilder:
    def build(self, verified_spec: VerifiedQuerySpec) -> BuiltQuery:
        spec = verified_spec.spec
        params: list[object] = []

        table_sql = self._quote_identifier(spec.target_table)
        if spec.mode == "count":
            select_sql = "COUNT(*) AS total_count"
        elif spec.select == ["*"]:
            select_sql = "*"
        else:
            select_sql = ", ".join(self._quote_identifier(field) for field in spec.select)

        where_clauses: list[str] = []
        for item in spec.filters:
            clause, clause_params = self._build_filter_clause(item)
            where_clauses.append(clause)
            params.extend(clause_params)

        search_clause, search_params = self._build_search_clause(spec.search)
        if search_clause:
            where_clauses.append(search_clause)
            params.extend(search_params)

        sql_parts = [f"SELECT {select_sql}", f"FROM {table_sql}"]
        if where_clauses:
            sql_parts.append("WHERE " + " AND ".join(where_clauses))

        if spec.mode == "list" and spec.sort:
            sql_parts.append("ORDER BY " + self._build_sort_clause(spec.sort))

        if spec.mode == "list":
            sql_parts.append("LIMIT ? OFFSET ?")
            params.append(spec.limit)
            params.append(spec.offset)

        sql = " ".join(sql_parts)
        reasoning = spec.reasoning or "generated from verified query spec"
        return BuiltQuery(
            sql=sql,
            params=list(params),
            selected_table=spec.target_table,
            reasoning=f"spec sql builder -> {reasoning}",
        )

    def _build_filter_clause(self, item: QueryFilter) -> tuple[str, list[object]]:
        field_sql = self._quote_identifier(item.field)
        op = item.op

        if op in {"=", "!=", ">", ">=", "<", "<="}:
            return f"{field_sql} {op} ?", [item.value]
        if op == "contains":
            return f"{field_sql} LIKE ?", [self._to_like_pattern(item.value)]
        if op == "not_contains":
            return f"{field_sql} NOT LIKE ?", [self._to_like_pattern(item.value)]
        if op == "in":
            if not isinstance(item.value, (list, tuple, set)) or len(item.value) == 0:
                raise ValueError("'in' filter requires a non-empty list value")
            values = list(item.value)
            placeholders = ", ".join("?" for _ in values)
            return f"{field_sql} IN ({placeholders})", values
        if op == "between":
            if item.value is None or item.value2 is None:
                raise ValueError("'between' filter requires value and value2")
            return f"{field_sql} BETWEEN ? AND ?", [item.value, item.value2]
        if op == "is_null":
            return f"{field_sql} IS NULL", []
        if op == "is_not_null":
            return f"{field_sql} IS NOT NULL", []

        raise ValueError(f"Unsupported filter op: {op}")

    def _build_search_clause(self, search: QuerySearch | None) -> tuple[str | None, list[object]]:
        if search is None or not search.query or not search.fields:
            return None, []

        pattern = self._to_like_pattern(search.query)
        fragments = [f"{self._quote_identifier(field)} LIKE ?" for field in search.fields]
        params = [pattern for _ in search.fields]
        return "(" + " OR ".join(fragments) + ")", params

    def _build_sort_clause(self, sort: list[QuerySort]) -> str:
        fragments = [f"{self._quote_identifier(item.field)} {item.direction.upper()}" for item in sort]
        return ", ".join(fragments)

    def _quote_identifier(self, identifier: str) -> str:
        escaped = identifier.replace('"', '""')
        return f'"{escaped}"'

    def _to_like_pattern(self, value: object) -> str:
        text = "" if value is None else str(value)
        return f"%{text}%"
