#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import sqlite3
from pathlib import Path
from typing import Iterable


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          city TEXT NOT NULL,
          segment TEXT NOT NULL,
          created_at TEXT NOT NULL
        );

        CREATE TABLE products (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          category TEXT NOT NULL,
          unit_price REAL NOT NULL,
          stock INTEGER NOT NULL
        );

        CREATE TABLE orders (
          id INTEGER PRIMARY KEY,
          customer_id INTEGER NOT NULL,
          product_id INTEGER NOT NULL,
          quantity INTEGER NOT NULL,
          amount REAL NOT NULL,
          status TEXT NOT NULL,
          ordered_at TEXT NOT NULL,
          FOREIGN KEY (customer_id) REFERENCES customers(id),
          FOREIGN KEY (product_id) REFERENCES products(id)
        );
        """
    )


def seed_customers() -> list[tuple[int, str, str, str, str]]:
    names = [
        "Liam", "Noah", "Olivia", "Emma", "Ava", "Mason", "Sophia", "Lucas", "Mia", "James",
        "Amelia", "Ethan", "Harper", "Evelyn", "Benjamin", "Elijah", "Isabella", "Henry", "Chloe", "Grace",
    ]
    cities = ["Shenzhen", "Shanghai", "Beijing", "Hangzhou", "Guangzhou"]
    segments = ["startup", "enterprise", "education", "retail"]

    rows: list[tuple[int, str, str, str, str]] = []
    for idx, name in enumerate(names, start=1):
        rows.append(
            (
                idx,
                name,
                random.choice(cities),
                random.choice(segments),
                f"2025-{(idx % 12) + 1:02d}-{(idx % 27) + 1:02d}",
            )
        )
    return rows


def seed_products() -> list[tuple[int, str, str, float, int]]:
    data = [
        (1, "Agent Notebook", "hardware", 1299.0, 42),
        (2, "Vector DB SaaS", "software", 399.0, 999),
        (3, "Prompt Toolkit", "software", 89.0, 999),
        (4, "Inference Box", "hardware", 4899.0, 15),
        (5, "Observability Pack", "software", 199.0, 260),
        (6, "Edge Sensor", "hardware", 599.0, 80),
        (7, "Training Credits", "service", 1599.0, 500),
        (8, "SQL Course", "service", 299.0, 400),
    ]
    return data


def seed_orders(num_orders: int, customer_ids: Iterable[int], product_rows: list[tuple[int, str, str, float, int]]) -> list[tuple[int, int, int, int, float, str, str]]:
    statuses = ["paid", "shipped", "completed", "refunded"]
    products = {row[0]: row for row in product_rows}
    customer_list = list(customer_ids)

    rows: list[tuple[int, int, int, int, float, str, str]] = []
    for order_id in range(1, num_orders + 1):
        customer_id = random.choice(customer_list)
        product_id = random.choice(list(products.keys()))
        quantity = random.randint(1, 6)
        unit_price = products[product_id][3]
        amount = round(unit_price * quantity * random.uniform(0.9, 1.1), 2)
        status = random.choices(statuses, weights=[3, 3, 6, 1], k=1)[0]
        month = ((order_id - 1) % 12) + 1
        day = ((order_id * 3) % 27) + 1
        ordered_at = f"2026-{month:02d}-{day:02d}"
        rows.append((order_id, customer_id, product_id, quantity, amount, status, ordered_at))
    return rows


def init_db(db_path: Path, num_orders: int, seed: int) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    random.seed(seed)

    with sqlite3.connect(db_path) as conn:
        create_schema(conn)

        customer_rows = seed_customers()
        product_rows = seed_products()
        order_rows = seed_orders(num_orders=num_orders, customer_ids=[row[0] for row in customer_rows], product_rows=product_rows)

        conn.executemany(
            "INSERT INTO customers (id, name, city, segment, created_at) VALUES (?, ?, ?, ?, ?)",
            customer_rows,
        )
        conn.executemany(
            "INSERT INTO products (id, name, category, unit_price, stock) VALUES (?, ?, ?, ?, ?)",
            product_rows,
        )
        conn.executemany(
            """
            INSERT INTO orders (id, customer_id, product_id, quantity, amount, status, ordered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            order_rows,
        )

        conn.commit()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a sample SQLite database for demos.")
    parser.add_argument("--db-path", default="sample_data/sample.sqlite", help="Output SQLite database path")
    parser.add_argument("--orders", type=int, default=120, help="Number of synthetic order rows")
    parser.add_argument("--seed", type=int, default=2026, help="Random seed for deterministic data")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    db_path = Path(args.db_path).resolve()
    init_db(db_path=db_path, num_orders=args.orders, seed=args.seed)
    print(f"Sample database initialized at: {db_path}")
    print("Tables: customers, products, orders")
    print(f"Rows: customers=20, products=8, orders={args.orders}")


if __name__ == "__main__":
    main()
