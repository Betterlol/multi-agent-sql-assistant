from __future__ import annotations

from ..types import GeneratedQuery, QueryFilter, QuerySearch, QuerySort, VerifiedQuerySpec


class SQLBuilder:
    def build(self, verified_spec: VerifiedQuerySpec) -> GeneratedQuery:
        spec = verified_spec.spec
        table_sql = self._quote_identifier(spec.target_table)

        if spec.mode == "count":
            select_sql = "COUNT(*) AS total_count"
        elif spec.select == ["*"]:
            select_sql = "*"
        else:
            select_sql = ", ".join(self._quote_identifier(field) for field in spec.select)

        where_clauses: list[str] = []
        where_clauses.extend(self._build_filter_clause(item) for item in spec.filters)
        search_clause = self._build_search_clause(spec.search)
        if search_clause:
            where_clauses.append(search_clause)

        sql_parts = [f"SELECT {select_sql}", f"FROM {table_sql}"]

        if where_clauses:
            sql_parts.append("WHERE " + " AND ".join(where_clauses))

        if spec.mode == "list" and spec.sort:
            sql_parts.append("ORDER BY " + self._build_sort_clause(spec.sort))

        if spec.mode == "list":
            sql_parts.append(f"LIMIT {spec.limit}")
            sql_parts.append(f"OFFSET {spec.offset}")

        sql = " ".join(sql_parts)
        reasoning = spec.reasoning or "generated from verified query spec"
        return GeneratedQuery(
            sql=sql,
            selected_table=spec.target_table,
            reasoning=f"spec sql builder -> {reasoning}",
        )

    def _build_filter_clause(self, item: QueryFilter) -> str:
        field_sql = self._quote_identifier(item.field)
        op = item.op

        if op in {"=", "!=", ">", ">=", "<", "<="}:
            return f"{field_sql} {op} {self._escape_literal(item.value)}"
        if op == "contains":
            return f"{field_sql} LIKE {self._escape_literal('%' + str(item.value) + '%')}"
        if op == "not_contains":
            return f"{field_sql} NOT LIKE {self._escape_literal('%' + str(item.value) + '%')}"
        if op == "in":
            if not isinstance(item.value, (list, tuple, set)) or len(item.value) == 0:
                raise ValueError("'in' filter requires a non-empty list value")
            rendered_values = ", ".join(self._escape_literal(value) for value in item.value)
            return f"{field_sql} IN ({rendered_values})"
        if op == "between":
            if item.value is None or item.value2 is None:
                raise ValueError("'between' filter requires value and value2")
            return (
                f"{field_sql} BETWEEN {self._escape_literal(item.value)} "
                f"AND {self._escape_literal(item.value2)}"
            )
        if op == "is_null":
            return f"{field_sql} IS NULL"
        if op == "is_not_null":
            return f"{field_sql} IS NOT NULL"

        raise ValueError(f"Unsupported filter op: {op}")

    def _build_search_clause(self, search: QuerySearch | None) -> str | None:
        if search is None or not search.query or not search.fields:
            return None

        pattern_sql = self._escape_literal(f"%{search.query}%")
        fragments = [f"{self._quote_identifier(field)} LIKE {pattern_sql}" for field in search.fields]
        return "(" + " OR ".join(fragments) + ")"

    def _build_sort_clause(self, sort: list[QuerySort]) -> str:
        fragments = [
            f"{self._quote_identifier(item.field)} {item.direction.upper()}"
            for item in sort
        ]
        return ", ".join(fragments)

    def _quote_identifier(self, identifier: str) -> str:
        escaped = identifier.replace('"', '""')
        return f'"{escaped}"'

    def _escape_literal(self, value: object) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"
