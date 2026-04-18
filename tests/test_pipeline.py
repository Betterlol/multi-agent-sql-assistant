from __future__ import annotations

import sqlite3
from pathlib import Path

from multi_agent_sql_assistant.database import SQLiteDatabaseClient
from multi_agent_sql_assistant.pipeline import SQLAssistantPipeline


def _prepare_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, amount REAL)")
        conn.executemany("INSERT INTO orders (amount) VALUES (?)", [(12.5,), (9.9,), (20.0,)])
        conn.commit()


def test_pipeline_generates_safe_count_query(tmp_path: Path) -> None:
    db_path = tmp_path / "sample.sqlite"
    _prepare_db(db_path)

    db_client = SQLiteDatabaseClient(str(db_path))
    schema = db_client.inspect_schema()

    pipeline = SQLAssistantPipeline()
    result = pipeline.run("How many orders are there?", schema=schema, max_rows=100)

    assert result.plan.intent == "count"
    assert "COUNT" in result.generated_query.sql.upper()
    assert result.generated_query.selected_table == "orders"
    assert result.verified_query.sql.lower().startswith("select")
