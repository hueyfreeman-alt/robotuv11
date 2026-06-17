import os
import sqlite3
from pathlib import Path

DB_NAME = os.getenv("DB_PATH", "shop.db")


def get_conn():
    db_path = Path(DB_NAME)
    if db_path.parent != Path("."):
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # PRODUCTS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT DEFAULT '',
        price REAL,
        stock INTEGER,
        category TEXT,
        type TEXT
    )
    """)

    # Add description column if missing (migration)
    try:
        cur.execute("ALTER TABLE products ADD COLUMN description TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    # PRODUCT DELIVERY ITEMS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS product_delivery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        delivery_type TEXT,
        content TEXT,
        file_id TEXT DEFAULT NULL,
        sort_order INTEGER DEFAULT 0,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)

    # CART
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        product_id INTEGER,
        quantity INTEGER
    )
    """)

    # ORDERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        total REAL,
        status TEXT,
        type TEXT
    )
    """)

    # ORDER ITEMS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER
    )
    """)

    # PAYMENTS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        amount REAL DEFAULT 0,
        provider TEXT,
        status TEXT,
        track_id TEXT,
        payment_url TEXT DEFAULT '',
        raw_status TEXT DEFAULT ''
    )
    """)

    for column, definition in (
        ("amount", "REAL DEFAULT 0"),
        ("track_id", "TEXT"),
        ("payment_url", "TEXT DEFAULT ''"),
        ("raw_status", "TEXT DEFAULT ''"),
    ):
        try:
            cur.execute(f"ALTER TABLE payments ADD COLUMN {column} {definition}")
        except sqlite3.OperationalError:
            pass

    cur.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_payments_track_id "
        "ON payments(track_id) WHERE track_id IS NOT NULL"
    )

    # SETTINGS (key-value store for admin config)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # BROADCASTS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        media_type TEXT,
        file_id TEXT,
        caption TEXT DEFAULT '',
        sent_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # USERS (track bot users for broadcasts)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        username TEXT DEFAULT '',
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
