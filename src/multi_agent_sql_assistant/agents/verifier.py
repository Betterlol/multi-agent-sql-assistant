from __future__ import annotations

import re

from ..database import DatabaseSchema
from ..types import VerifiedQuery


class SQLVerificationError(ValueError):
    pass


class VerifierAgent:
    _BLOCKED_KEYWORDS = {
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "attach",
        "detach",
        "pragma",
        "vacuum",
        "replace",
        "truncate",
    }

    def verify(self, sql: str, schema: DatabaseSchema, max_limit: int = 100) -> VerifiedQuery:
        cleaned = sql.strip()
        if not cleaned:
            raise SQLVerificationError("Generated SQL is empty.")

        cleaned = self._ensure_single_statement(cleaned)
        self._ensure_read_only(cleaned)
        self._ensure_tables_exist(cleaned, schema)

        warnings: list[str] = []
        final_sql, limit_warning = self._enforce_limit(cleaned, max_limit=max_limit)
        if limit_warning:
            warnings.append(limit_warning)

        return VerifiedQuery(sql=final_sql, warnings=warnings)

    def _ensure_single_statement(self, sql: str) -> str:
        trimmed = sql.rstrip(";").strip()
        if ";" in trimmed:
            raise SQLVerificationError("Multiple SQL statements are not allowed.")
        return trimmed

    def _ensure_read_only(self, sql: str) -> None:
        lowered = sql.lower()
        if not (lowered.startswith("select") or lowered.startswith("with")):
            raise SQLVerificationError("Only read-only SELECT queries are allowed.")

        for keyword in self._BLOCKED_KEYWORDS:
            if re.search(rf"\b{keyword}\b", lowered):
                raise SQLVerificationError(f"Blocked keyword detected: {keyword}")

    def _ensure_tables_exist(self, sql: str, schema: DatabaseSchema) -> None:
        referenced = re.findall(r'\b(?:from|join)\s+["`]?([a-zA-Z_][\w]*)', sql, flags=re.IGNORECASE)
        missing = [table for table in referenced if table not in schema.tables]
        if missing:
            raise SQLVerificationError(f"Unknown table(s): {', '.join(sorted(set(missing)))}")

    def _enforce_limit(self, sql: str, max_limit: int) -> tuple[str, str | None]:
        limit_match = re.search(r"\blimit\s+(\d+)\b", sql, flags=re.IGNORECASE)
        if limit_match:
            original_limit = int(limit_match.group(1))
            if original_limit <= max_limit:
                return sql, None

            bounded_sql = re.sub(
                r"\blimit\s+\d+\b",
                f"LIMIT {max_limit}",
                sql,
                flags=re.IGNORECASE,
                count=1,
            )
            return bounded_sql, f"LIMIT reduced from {original_limit} to {max_limit}."

        return f"{sql} LIMIT {max_limit}", f"LIMIT added: {max_limit}."
