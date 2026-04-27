from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from multi_agent_sql_assistant.agents.spec_verifier import QuerySpecVerificationError, QuerySpecVerifier
from multi_agent_sql_assistant.agents.sql_builder import SQLBuilder
from multi_agent_sql_assistant.database import DatabaseSchema, SQLiteDatabaseClient
from multi_agent_sql_assistant.pipeline import SQLAssistantPipeline
from multi_agent_sql_assistant.types import QueryFilter, QuerySearch, QuerySort, QuerySpec


def _schema() -> DatabaseSchema:
    return DatabaseSchema(
        tables={
            "works": ["id", "title", "description", "rating", "updated_at"],
            "orders": ["id", "amount", "updated_at", "note"],
        }
    )


# QuerySpecVerifier tests

def test_spec_verifier_rejects_unknown_table() -> None:
    verifier = QuerySpecVerifier()
    spec = QuerySpec(target_table="missing")

    with pytest.raises(QuerySpecVerificationError):
        verifier.verify(spec=spec, schema=_schema(), max_limit=100)


def test_spec_verifier_rejects_unknown_field() -> None:
    verifier = QuerySpecVerifier()
    spec = QuerySpec(target_table="works", select=["missing"])

    with pytest.raises(QuerySpecVerificationError):
        verifier.verify(spec=spec, schema=_schema(), max_limit=100)


def test_spec_verifier_clamps_limit_and_adds_warning() -> None:
    verifier = QuerySpecVerifier()
    spec = QuerySpec(target_table="works", limit=1000)

    verified = verifier.verify(spec=spec, schema=_schema(), max_limit=100)

    assert verified.spec.limit == 100
    assert any("limit reduced" in warning for warning in verified.warnings)


def test_spec_verifier_rejects_invalid_operator() -> None:
    verifier = QuerySpecVerifier()
    spec = QuerySpec(
        target_table="works",
        filters=[QueryFilter(field="rating", op="bad_op", value=1)],
    )

    with pytest.raises(QuerySpecVerificationError):
        verifier.verify(spec=spec, schema=_schema(), max_limit=100)


def test_spec_verifier_rejects_invalid_sort_direction() -> None:
    verifier = QuerySpecVerifier()
    spec = QuerySpec(
        target_table="works",
        sort=[QuerySort(field="updated_at", direction="up")],
    )

    with pytest.raises(QuerySpecVerificationError):
        verifier.verify(spec=spec, schema=_schema(), max_limit=100)


# SQLBuilder tests

def _build_sql(spec: QuerySpec) -> str:
    verified = QuerySpecVerifier().verify(spec=spec, schema=_schema(), max_limit=100)
    built = SQLBuilder().build(verified)
    return built.sql


def test_sql_builder_contains_generates_like() -> None:
    sql = _build_sql(
        QuerySpec(
            target_table="works",
            filters=[QueryFilter(field="title", op="contains", value="dragon")],
        )
    )
    assert '"title" LIKE \'%dragon%\'' in sql


def test_sql_builder_in_generates_in_list() -> None:
    sql = _build_sql(
        QuerySpec(
            target_table="works",
            filters=[QueryFilter(field="id", op="in", value=[1, 2, 3])],
        )
    )
    assert '"id" IN (1, 2, 3)' in sql


def test_sql_builder_between_generates_between_clause() -> None:
    sql = _build_sql(
        QuerySpec(
            target_table="works",
            filters=[QueryFilter(field="rating", op="between", value=5, value2=8)],
        )
    )
    assert '"rating" BETWEEN 5 AND 8' in sql


def test_sql_builder_search_multi_fields_generates_or() -> None:
    sql = _build_sql(
        QuerySpec(
            target_table="works",
            search=QuerySearch(query="dragon", fields=["title", "description"]),
        )
    )
    assert '("title" LIKE \'%dragon%\'' in sql
    assert 'OR "description" LIKE \'%dragon%\'' in sql


def test_sql_builder_count_mode_generates_count() -> None:
    sql = _build_sql(QuerySpec(target_table="works", mode="count"))
    assert sql.startswith('SELECT COUNT(*) AS total_count FROM "works"')


def test_sql_builder_escapes_single_quotes() -> None:
    sql = _build_sql(
        QuerySpec(
            target_table="works",
            filters=[QueryFilter(field="title", op="contains", value="O'Hara")],
        )
    )
    assert "'%O''Hara%'" in sql


# Pipeline tests

def _prepare_orders_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, amount REAL, updated_at TEXT, note TEXT)")
        conn.executemany(
            "INSERT INTO orders (amount, updated_at, note) VALUES (?, ?, ?)",
            [
                (10.0, "2026-04-20T10:00:00", "alpha"),
                (25.0, "2026-04-21T10:00:00", "beta"),
                (15.0, "2026-04-22T10:00:00", "gamma"),
            ],
        )
        conn.commit()


def test_pipeline_runs_list_query_without_llm(tmp_path: Path) -> None:
    db_path = tmp_path / "sample.sqlite"
    _prepare_orders_db(db_path)

    schema = SQLiteDatabaseClient(str(db_path)).inspect_schema()
    result = SQLAssistantPipeline().run("List orders", schema=schema, max_rows=50)

    assert result.query_spec.mode == "list"
    assert result.generated_query.selected_table == "orders"
    assert result.verified_query.sql.lower().startswith("select")


def test_pipeline_count_query_generates_count_sql(tmp_path: Path) -> None:
    db_path = tmp_path / "sample.sqlite"
    _prepare_orders_db(db_path)

    schema = SQLiteDatabaseClient(str(db_path)).inspect_schema()
    result = SQLAssistantPipeline().run("How many orders are there?", schema=schema, max_rows=50)

    assert result.query_spec.mode == "count"
    assert "COUNT(*)" in result.generated_query.sql.upper()


def test_pipeline_top_query_generates_order_by_desc_and_limit(tmp_path: Path) -> None:
    db_path = tmp_path / "sample.sqlite"
    _prepare_orders_db(db_path)

    schema = SQLiteDatabaseClient(str(db_path)).inspect_schema()
    result = SQLAssistantPipeline().run("Top 2 orders by amount", schema=schema, max_rows=50)

    sql_upper = result.generated_query.sql.upper()
    assert result.query_spec.mode == "list"
    assert "ORDER BY" in sql_upper
    assert "DESC" in sql_upper
    assert "LIMIT 2" in sql_upper
