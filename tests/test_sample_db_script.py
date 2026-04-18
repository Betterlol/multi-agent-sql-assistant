from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path


def test_init_sample_db_script_creates_expected_tables(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "init_sample_db.py"
    db_path = tmp_path / "demo.sqlite"

    subprocess.run(
        [
            sys.executable,
            str(script),
            "--db-path",
            str(db_path),
            "--orders",
            "40",
            "--seed",
            "2026",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert db_path.exists()

    with sqlite3.connect(db_path) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert {"customers", "products", "orders"}.issubset(tables)

        customer_count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

        assert customer_count == 20
        assert product_count == 8
        assert order_count == 40
