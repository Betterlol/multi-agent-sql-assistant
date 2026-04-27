from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .types import QueryResult


@dataclass(frozen=True)
class DatabaseSchema:
    tables: dict[str, list[str]]


class SQLiteDatabaseClient:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def _connect(self) -> sqlite3.Connection:
        if self.database_path != ":memory:":
            path = Path(self.database_path)
            if not path.exists():
                raise FileNotFoundError(f"Database file does not exist: {self.database_path}")
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def inspect_schema(self) -> DatabaseSchema:
        with self._connect() as conn:
            table_rows = conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()

            tables: dict[str, list[str]] = {}
            for row in table_rows:
                table = str(row["name"])
                columns = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
                tables[table] = [str(col["name"]) for col in columns]

        return DatabaseSchema(tables=tables)

    def execute_query(
        self,
        sql: str,
        params: list[Any] | tuple[Any, ...] | None = None,
        max_rows: int = 100,
    ) -> QueryResult:
        with self._connect() as conn:
            if params is None:
                cursor = conn.execute(sql)
            else:
                cursor = conn.execute(sql, tuple(params))
            rows = cursor.fetchmany(max_rows)
            columns = [str(desc[0]) for desc in cursor.description or []]
            serialized_rows: list[list[Any]] = []
            for row in rows:
                serialized_rows.append([row[col] for col in columns])

        return QueryResult(columns=columns, rows=serialized_rows)
