import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_NAME = "shop.db"


@contextmanager
def get_conn():
    """Context manager that provides a database connection with automatic cleanup."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        yield conn
    except sqlite3.Error as e:
        logger.error("Database connection error: %s", e)
        raise
    finally:
        if conn:
            conn.close()


def init_db():
    """Initialize database tables. Raises on failure so the bot won't start with a broken DB."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()

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

            cur.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                product_id INTEGER,
                quantity INTEGER
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                total REAL,
                status TEXT,
                type TEXT
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                provider TEXT,
                status TEXT
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_type TEXT,
                file_id TEXT,
                caption TEXT DEFAULT '',
                sent_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT DEFAULT '',
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """)

            conn.commit()
            logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.critical("Failed to initialize database: %s", e)
        raise RuntimeError(f"Database initialization failed: {e}") from e
