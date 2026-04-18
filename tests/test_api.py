from __future__ import annotations

import sqlite3
from io import BytesIO
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
    assert "request_id" in data
    assert data["selected_table"] == "orders"
    assert data["row_count"] >= 1
    assert "verified_sql" in data


def test_upload_then_query_by_database_id(tmp_path: Path) -> None:
    fastapi = pytest.importorskip("fastapi")
    _ = fastapi
    from fastapi.testclient import TestClient

    from multi_agent_sql_assistant.app import create_app

    db_path = tmp_path / "upload.sqlite"
    _prepare_db(db_path)
    db_bytes = db_path.read_bytes()

    app = create_app()
    client = TestClient(app)

    upload_response = client.post(
        "/v1/upload-db",
        files={"file": ("upload.sqlite", BytesIO(db_bytes), "application/octet-stream")},
    )
    assert upload_response.status_code == 200
    uploaded = upload_response.json()
    assert "request_id" in uploaded
    assert "database_id" in uploaded
    assert uploaded["table_count"] >= 1
    assert "expires_at" in uploaded

    query_payload = {
        "database_id": uploaded["database_id"],
        "question": "How many orders are there?",
        "max_rows": 20,
    }
    query_response = client.post("/v1/query", json=query_payload)
    assert query_response.status_code == 200
    data = query_response.json()
    assert "request_id" in data
    assert data["selected_table"] == "orders"
    assert data["row_count"] >= 1


def test_query_requires_database_source() -> None:
    fastapi = pytest.importorskip("fastapi")
    _ = fastapi
    from fastapi.testclient import TestClient

    from multi_agent_sql_assistant.app import create_app

    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/v1/query",
        json={"question": "How many orders are there?", "max_rows": 20},
    )

    assert response.status_code == 422


def test_query_with_enabled_llm_requires_api_key_when_env_missing(tmp_path: Path, monkeypatch) -> None:
    fastapi = pytest.importorskip("fastapi")
    _ = fastapi
    from fastapi.testclient import TestClient

    from multi_agent_sql_assistant.app import create_app

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    db_path = tmp_path / "llm.sqlite"
    _prepare_db(db_path)

    app = create_app()
    client = TestClient(app)

    payload = {
        "database_path": str(db_path),
        "question": "How many orders are there?",
        "max_rows": 20,
        "llm": {"enabled": True, "provider": "openai"},
    }
    response = client.post("/v1/query", json=payload)

    assert response.status_code == 400
    assert "API key is missing" in response.json()["detail"]


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
    assert "选择 SQLite 文件" in response.text
    assert "LLM 配置（可选）" in response.text


def test_metrics_endpoint_tracks_query_and_upload(tmp_path: Path) -> None:
    fastapi = pytest.importorskip("fastapi")
    _ = fastapi
    from fastapi.testclient import TestClient

    from multi_agent_sql_assistant.app import create_app

    db_path = tmp_path / "metrics.sqlite"
    _prepare_db(db_path)
    db_bytes = db_path.read_bytes()

    app = create_app()
    client = TestClient(app)

    before = client.get("/metrics")
    assert before.status_code == 200
    before_metrics = before.json()

    upload = client.post(
        "/v1/upload-db",
        files={"file": ("metrics.sqlite", BytesIO(db_bytes), "application/octet-stream")},
    )
    assert upload.status_code == 200
    upload_data = upload.json()

    query = client.post(
        "/v1/query",
        json={
            "database_id": upload_data["database_id"],
            "question": "How many orders are there?",
            "max_rows": 20,
        },
    )
    assert query.status_code == 200

    after = client.get("/metrics")
    assert after.status_code == 200
    after_metrics = after.json()
    assert after_metrics["uploads_total"] >= before_metrics["uploads_total"] + 1
    assert after_metrics["queries_total"] >= before_metrics["queries_total"] + 1
