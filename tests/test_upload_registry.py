from __future__ import annotations

import sqlite3
from pathlib import Path

from multi_agent_sql_assistant.upload_registry import UploadRegistry


def _make_sqlite_bytes(path: Path) -> bytes:
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO t (name) VALUES ('a')")
        conn.commit()
    return path.read_bytes()


def test_registry_persists_and_resolves_uploaded_path(tmp_path: Path) -> None:
    root = tmp_path / "uploads"
    sqlite_src = tmp_path / "sample.sqlite"
    payload = _make_sqlite_bytes(sqlite_src)

    registry = UploadRegistry(root_dir=root, ttl_seconds=3600)
    record = registry.register(filename="sample.sqlite", payload=payload)

    restarted_registry = UploadRegistry(root_dir=root, ttl_seconds=3600)
    resolved = restarted_registry.resolve_path(record.database_id)

    assert resolved is not None
    assert resolved.exists()
    assert resolved.read_bytes() == payload


def test_registry_cleanup_removes_expired_records(tmp_path: Path) -> None:
    root = tmp_path / "uploads"
    sqlite_src = tmp_path / "sample.sqlite"
    payload = _make_sqlite_bytes(sqlite_src)

    registry = UploadRegistry(root_dir=root, ttl_seconds=3600)
    record = registry.register(filename="sample.sqlite", payload=payload)
    stored = record.stored_path

    with sqlite3.connect(registry.db_path) as conn:
        conn.execute("UPDATE uploads SET expires_at = 0 WHERE database_id = ?", (record.database_id,))
        conn.commit()

    removed = registry.cleanup_expired()
    assert removed >= 1
    assert registry.resolve_path(record.database_id) is None
    assert not stored.exists()
