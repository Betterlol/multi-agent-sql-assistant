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
class QueryFilter:
    field: str
    op: str
    value: Any | None = None
    value2: Any | None = None


@dataclass(frozen=True)
class QuerySort:
    field: str
    direction: str = "asc"


@dataclass(frozen=True)
class QuerySearch:
    query: str
    fields: list[str]


@dataclass(frozen=True)
class QuerySpec:
    target_table: str
    select: list[str] = field(default_factory=lambda: ["*"])
    filters: list[QueryFilter] = field(default_factory=list)
    search: QuerySearch | None = None
    sort: list[QuerySort] = field(default_factory=list)
    limit: int = 20
    offset: int = 0
    mode: str = "list"
    reasoning: str = ""


@dataclass(frozen=True)
class VerifiedQuerySpec:
    spec: QuerySpec
    warnings: list[str] = field(default_factory=list)


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
