from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from multi_agent_sql_assistant.agents.spec_verifier import QuerySpecVerificationError, QuerySpecVerifier
from multi_agent_sql_assistant.agents.sql_builder import SQLBuilder
from multi_agent_sql_assistant.database import DatabaseSchema, SQLiteDatabaseClient
from multi_agent_sql_assistant.pipeline import SQLAssistantPipeline
from multi_agent_sql_assistant.schema_semantics import build_default_semantics
from multi_agent_sql_assistant.types import QueryFilter, QuerySearch, QuerySort, QuerySpec


def _schema() -> DatabaseSchema:
    return DatabaseSchema(
        tables={
            "works": ["id", "title", "description", "rating", "updated_at"],
            "orders": ["id", "amount", "updated_at", "note"],
        }
    )


def _prepare_works_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE works (id INTEGER PRIMARY KEY, title TEXT, description TEXT, rating REAL, updated_at TEXT)"
        )
        conn.executemany(
            "INSERT INTO works (title, description, rating, updated_at) VALUES (?, ?, ?, ?)",
            [
                ("Dragon Ball", "martial arts story", 9.1, "2026-04-21T10:00:00"),
                ("One Piece", "pirate adventure", 9.5, "2026-04-22T10:00:00"),
                ("Bleach", "soul reaper", 8.0, "2026-04-20T10:00:00"),
            ],
        )
        conn.commit()


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


def test_spec_verifier_search_fields_fallback_to_searchable_fields() -> None:
    verifier = QuerySpecVerifier()
    spec = QuerySpec(
        target_table="works",
        search=QuerySearch(query="dragon", fields=[]),
    )

    verified = verifier.verify(spec=spec, schema=_schema(), max_limit=100)

    assert verified.spec.search is not None
    assert set(verified.spec.search.fields) == {"title", "description"}


# semantics tests

def test_build_default_semantics_marks_searchable_and_sortable_fields() -> None:
    semantics = build_default_semantics(_schema())
    works = semantics.tables["works"]

    assert works.fields["title"].searchable is True
    assert works.fields["updated_at"].sortable is True
    assert works.fields["rating"].sortable is True


# SQLBuilder parameterization tests

def _build_query(spec: QuerySpec):
    verified = QuerySpecVerifier().verify(spec=spec, schema=_schema(), max_limit=100)
    return SQLBuilder().build(verified)


def test_sql_builder_contains_parameterized_like() -> None:
    built = _build_query(
        QuerySpec(
            target_table="works",
            filters=[QueryFilter(field="title", op="contains", value="dragon")],
        )
    )
    assert '"title" LIKE ?' in built.sql
    assert "dragon" not in built.sql.lower()
    assert "%dragon%" in built.params


def test_sql_builder_in_parameterized_placeholders() -> None:
    built = _build_query(
        QuerySpec(
            target_table="works",
            filters=[QueryFilter(field="id", op="in", value=[1, 2, 3])],
        )
    )
    assert '"id" IN (?, ?, ?)' in built.sql
    assert built.params[:3] == [1, 2, 3]


def test_sql_builder_between_parameterized() -> None:
    built = _build_query(
        QuerySpec(
            target_table="works",
            filters=[QueryFilter(field="rating", op="between", value=5, value2=8)],
        )
    )
    assert '"rating" BETWEEN ? AND ?' in built.sql
    assert built.params[:2] == [5, 8]


def test_sql_builder_search_multi_fields_generates_or_parameterized() -> None:
    built = _build_query(
        QuerySpec(
            target_table="works",
            search=QuerySearch(query="dragon", fields=["title", "description"]),
        )
    )
    assert '("title" LIKE ? OR "description" LIKE ?)' in built.sql
    assert built.params[:2] == ["%dragon%", "%dragon%"]


def test_sql_builder_count_mode_generates_count() -> None:
    built = _build_query(QuerySpec(target_table="works", mode="count"))
    assert built.sql.startswith('SELECT COUNT(*) AS total_count FROM "works"')


def test_sql_builder_params_include_limit_and_offset() -> None:
    built = _build_query(QuerySpec(target_table="works", limit=50, offset=10, mode="list"))
    assert "LIMIT ? OFFSET ?" in built.sql
    assert built.params[-2:] == [50, 10]


# database parameterized execute test

def test_database_execute_query_supports_params(tmp_path: Path) -> None:
    db_path = tmp_path / "works.sqlite"
    _prepare_works_db(db_path)
    db_client = SQLiteDatabaseClient(str(db_path))

    result = db_client.execute_query(
        'SELECT "title" FROM "works" WHERE "title" LIKE ? ORDER BY "id" LIMIT ? OFFSET ?',
        params=["%dragon%", 10, 0],
        max_rows=10,
    )

    assert result.row_count == 1
    assert result.rows[0][0] == "Dragon Ball"


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
    assert result.built_query.selected_table == "orders"
    assert result.verified_query.sql.lower().startswith("select")
    assert "LIMIT ? OFFSET ?" in result.built_query.sql


def test_pipeline_count_query_generates_count_sql(tmp_path: Path) -> None:
    db_path = tmp_path / "sample.sqlite"
    _prepare_orders_db(db_path)

    schema = SQLiteDatabaseClient(str(db_path)).inspect_schema()
    result = SQLAssistantPipeline().run("How many orders are there?", schema=schema, max_rows=50)

    assert result.query_spec.mode == "count"
    assert "COUNT(*)" in result.built_query.sql.upper()


def test_pipeline_top_query_generates_order_by_desc_and_parameterized_limit(tmp_path: Path) -> None:
    db_path = tmp_path / "sample.sqlite"
    _prepare_orders_db(db_path)

    schema = SQLiteDatabaseClient(str(db_path)).inspect_schema()
    result = SQLAssistantPipeline().run("Top 2 orders by amount", schema=schema, max_rows=50)

    sql_upper = result.built_query.sql.upper()
    assert result.query_spec.mode == "list"
    assert "ORDER BY" in sql_upper
    assert "DESC" in sql_upper
    assert "LIMIT ? OFFSET ?" in sql_upper
    assert result.built_query.params[-2:] == [2, 0]
