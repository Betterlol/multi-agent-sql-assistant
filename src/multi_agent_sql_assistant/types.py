from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class QueryPlan:
    intent: str
    table_hint: str | None = None
    limit: int = 20
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GeneratedQuery:
    sql: str
    selected_table: str
    reasoning: str


@dataclass(frozen=True)
class VerifiedQuery:
    sql: str
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[list[Any]]

    @property
    def row_count(self) -> int:
        return len(self.rows)
