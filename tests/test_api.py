from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


def _prepare_db(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, amount REAL)")
        conn.executemany("INSERT INTO orders (amount) VALUES (?)", [(100.0,), (55.5,), (8.2,)])
        conn.commit()


def test_query_endpoint_returns_rows(tmp_path: Path) -> None:
    fastapi = pytest.importorskip("fastapi")
    _ = fastapi  # silence lint for explicit importorskip intent
    from fastapi.testclient import TestClient

    from multi_agent_sql_assistant.app import create_app

    db_path = tmp_path / "api.sqlite"
    _prepare_db(db_path)

    app = create_app()
    client = TestClient(app)

    payload = {
        "database_path": str(db_path),
        "question": "List top 2 orders by amount",
        "max_rows": 20,
    }
    response = client.post("/v1/query", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["selected_table"] == "orders"
    assert data["row_count"] >= 1
    assert "verified_sql" in data


def test_index_page_served() -> None:
    fastapi = pytest.importorskip("fastapi")
    _ = fastapi
    from fastapi.testclient import TestClient

    from multi_agent_sql_assistant.app import create_app

    app = create_app()
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert "Multi-Agent SQL Assistant" in response.text
    assert "/static/styles.css" in response.text
