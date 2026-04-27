from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from utils.io_helpers import ensure_dir, load_yaml


CUSTOMERS = [
    {"customer_id": 1, "full_name": "Alice Johnson", "email": "ALICE@example.com ", "country": "usa", "signup_ts": "2024-01-10 10:15:00"},
    {"customer_id": 2, "full_name": " Bob Smith", "email": "bob.smith@example.com", "country": "USA", "signup_ts": "2024-01-11 12:00:00"},
    {"customer_id": 3, "full_name": "Carlos Diaz", "email": "carlos@example.com", "country": "mexico", "signup_ts": "2024-01-12 09:30:00"},
    {"customer_id": 4, "full_name": "Diana Prince", "email": "diana@example.com", "country": "india", "signup_ts": "2024-01-13 14:40:00"},
    {"customer_id": 5, "full_name": "Evelyn Stone", "email": "evelyn@example.com", "country": "uk", "signup_ts": "2024-01-14 17:05:00"},
    {"customer_id": 6, "full_name": "Farhan Ali", "email": "farhan@example.com", "country": "uae", "signup_ts": "2024-01-15 18:20:00"},
]

ORDERS = [
    (1001, 1, "Laptop", 1200.0, "DONE", "2024-02-01 08:00:00"),
    (1002, 1, "Mouse", 25.5, "PENDING_APPROVAL", "2024-02-01 09:00:00"),
    (1003, 2, "Keyboard", 70.0, "DONE", "2024-02-02 10:00:00"),
    (1004, 3, "Monitor", 300.0, "FAILED", "2024-02-03 11:00:00"),
    (1005, 4, "Desk", 500.0, "DONE", "2024-02-04 12:30:00"),
    (1006, 5, "Chair", 220.0, "PENDING_APPROVAL", "2024-02-05 13:30:00"),
    (1007, 6, "Dock", 180.0, "DONE", "2024-02-06 14:30:00"),
    (1008, 2, "Webcam", 95.0, "DONE", "2024-02-07 15:30:00"),
]


def main() -> None:
    config = load_yaml("configs/app_config.yaml")
    csv_path = Path(config["paths"]["source_csv"])
    sqlite_path = Path(config["paths"]["source_sqlite"])

    ensure_dir(csv_path.parent)
    customers_df = pd.DataFrame(CUSTOMERS)
    customers_df.to_csv(csv_path, index=False)

    if sqlite_path.exists():
        sqlite_path.unlink()

    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_ref INTEGER,
            product_name TEXT,
            order_amount REAL,
            order_status TEXT,
            created_at TEXT
        )
        """
    )
    cur.executemany(
        "INSERT INTO orders (order_id, customer_ref, product_name, order_amount, order_status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        ORDERS,
    )
    conn.commit()
    conn.close()

    print(f"Created CSV source at: {csv_path}")
    print(f"Created SQLite source at: {sqlite_path}")
    print(f"Customers rows: {len(CUSTOMERS)}")
    print(f"Orders rows: {len(ORDERS)}")


if __name__ == "__main__":
    main()
