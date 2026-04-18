from __future__ import annotations

import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class UploadRecord:
    database_id: str
    filename: str
    stored_path: Path
    created_at: int
    expires_at: int
    size_bytes: int


class UploadRegistry:
    def __init__(self, root_dir: Path, ttl_seconds: int) -> None:
        self.root_dir = root_dir
        self.ttl_seconds = max(ttl_seconds, 1)
        self.files_dir = self.root_dir / "files"
        self.db_path = self.root_dir / "registry.sqlite"
        self._lock = threading.Lock()

        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def register(self, filename: str, payload: bytes) -> UploadRecord:
        now = int(time.time())
        database_id = uuid4().hex
        stored_path = self.files_dir / f"{database_id}.sqlite"
        stored_path.write_bytes(payload)
        expires_at = now + self.ttl_seconds
        size_bytes = len(payload)

        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO uploads (database_id, filename, stored_path, created_at, expires_at, size_bytes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (database_id, filename, str(stored_path), now, expires_at, size_bytes),
            )
            conn.commit()

        return UploadRecord(
            database_id=database_id,
            filename=filename,
            stored_path=stored_path,
            created_at=now,
            expires_at=expires_at,
            size_bytes=size_bytes,
        )

    def resolve_path(self, database_id: str) -> Path | None:
        self.cleanup_expired()
        now = int(time.time())
        with self._lock, self._connect() as conn:
            row = conn.execute(
                """
                SELECT database_id, filename, stored_path, created_at, expires_at, size_bytes
                FROM uploads
                WHERE database_id = ?
                """,
                (database_id,),
            ).fetchone()
            if row is None:
                return None

            expires_at = int(row["expires_at"])
            stored_path = Path(str(row["stored_path"]))
            if expires_at < now or not stored_path.exists():
                self._delete_record(conn, database_id, stored_path)
                conn.commit()
                return None

            return stored_path

    def cleanup_expired(self) -> int:
        now = int(time.time())
        removed = 0
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT database_id, stored_path
                FROM uploads
                WHERE expires_at < ?
                """,
                (now,),
            ).fetchall()
            for row in rows:
                database_id = str(row["database_id"])
                stored_path = Path(str(row["stored_path"]))
                self._delete_record(conn, database_id, stored_path)
                removed += 1
            if rows:
                conn.commit()
        return removed

    def active_count(self) -> int:
        self.cleanup_expired()
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM uploads").fetchone()
            assert row is not None
            return int(row["c"])

    def remove(self, database_id: str) -> None:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT stored_path FROM uploads WHERE database_id = ?",
                (database_id,),
            ).fetchone()
            if row is None:
                return
            stored_path = Path(str(row["stored_path"]))
            self._delete_record(conn, database_id, stored_path)
            conn.commit()

    def _init_schema(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS uploads (
                    database_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    stored_path TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    size_bytes INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _delete_record(self, conn: sqlite3.Connection, database_id: str, stored_path: Path) -> None:
        conn.execute("DELETE FROM uploads WHERE database_id = ?", (database_id,))
        stored_path.unlink(missing_ok=True)
