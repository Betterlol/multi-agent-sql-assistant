from __future__ import annotations

from typing import Any

import sqlglot
from sqlglot import exp

from ..database import DatabaseSchema
from ..types import VerifiedQuery


class SQLVerificationError(ValueError):
    pass


class VerifierAgent:
    _MUTATING_TYPES = tuple(
        expression_type
        for expression_type in (
            getattr(exp, "Insert", None),
            getattr(exp, "Update", None),
            getattr(exp, "Delete", None),
            getattr(exp, "Create", None),
            getattr(exp, "Drop", None),
            getattr(exp, "Alter", None),
            getattr(exp, "TruncateTable", None),
            getattr(exp, "Command", None),
            getattr(exp, "Merge", None),
        )
        if expression_type is not None
    )

    def verify(self, sql: str, schema: DatabaseSchema, max_limit: int = 100) -> VerifiedQuery:
        cleaned = sql.strip()
        if not cleaned:
            raise SQLVerificationError("Generated SQL is empty.")

        parsed = self._parse_single_statement(cleaned)
        self._ensure_read_only(parsed)
        self._ensure_tables_exist(parsed, schema)

        warnings: list[str] = []
        final_sql, limit_warning = self._enforce_limit(parsed, max_limit=max_limit)
        if limit_warning:
            warnings.append(limit_warning)

        return VerifiedQuery(sql=final_sql, warnings=warnings)

    def _parse_single_statement(self, sql: str) -> exp.Expression:
        try:
            statements = sqlglot.parse(sql, read="sqlite")
        except sqlglot.errors.ParseError as exc:
            raise SQLVerificationError(f"Invalid SQL syntax: {exc}") from exc

        if not statements:
            raise SQLVerificationError("SQL parse result is empty.")
        if len(statements) != 1:
            raise SQLVerificationError("Multiple SQL statements are not allowed.")
        return statements[0]

    def _ensure_read_only(self, statement: exp.Expression) -> None:
        if not isinstance(statement, exp.Query):
            raise SQLVerificationError("Only read-only SELECT queries are allowed.")

        if self._MUTATING_TYPES and any(statement.find(m_type) for m_type in self._MUTATING_TYPES):
            raise SQLVerificationError("Mutating SQL is not allowed.")

    def _ensure_tables_exist(self, statement: exp.Expression, schema: DatabaseSchema) -> None:
        existing = {table.lower(): table for table in schema.tables}
        missing: list[str] = []
        for table in statement.find_all(exp.Table):
            if table.name is None:
                continue
            if table.name.lower() not in existing:
                missing.append(table.name)

        if missing:
            raise SQLVerificationError(f"Unknown table(s): {', '.join(sorted(set(missing)))}")

    def _enforce_limit(self, statement: exp.Expression, max_limit: int) -> tuple[str, str | None]:
        query = statement
        if not isinstance(query, exp.Query):
            raise SQLVerificationError("Only query expressions support LIMIT enforcement.")

        bounded = query.copy()
        limit_node = bounded.args.get("limit")
        existing_limit = self._extract_limit_value(limit_node)

        if existing_limit is not None and existing_limit <= max_limit:
            return bounded.sql(dialect="sqlite"), None

        bounded = bounded.limit(max_limit, copy=False)
        if existing_limit is None:
            warning = f"LIMIT added: {max_limit}."
        else:
            warning = f"LIMIT reduced from {existing_limit} to {max_limit}."

        return bounded.sql(dialect="sqlite"), warning

    def _extract_limit_value(self, limit_expr: Any) -> int | None:
        if limit_expr is None:
            return None

        try:
            value_node = limit_expr.expression
        except AttributeError:
            return None
        if not isinstance(value_node, exp.Literal):
            return None
        if not value_node.is_int:
            return None
        return int(value_node.this)
