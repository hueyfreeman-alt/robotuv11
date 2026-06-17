import sqlite3
from unittest.mock import patch

import db.database as database_mod
from db.database import get_conn, init_db


class TestGetConn:
    def test_returns_sqlite_connection(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            conn = get_conn()
            assert isinstance(conn, sqlite3.Connection)
            conn.close()


class TestInitDb:
    def test_creates_products_table(self, db_conn):
        cur = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='products'"
        )
        assert cur.fetchone() is not None

    def test_products_table_columns(self, db_conn):
        cur = db_conn.execute("PRAGMA table_info(products)")
        cols = {row[1] for row in cur.fetchall()}
        assert cols == {"id", "name", "description", "price", "stock", "category", "type"}

    def test_creates_product_delivery_table(self, db_conn):
        cur = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='product_delivery'"
        )
        assert cur.fetchone() is not None

    def test_product_delivery_columns(self, db_conn):
        cur = db_conn.execute("PRAGMA table_info(product_delivery)")
        cols = {row[1] for row in cur.fetchall()}
        assert cols == {"id", "product_id", "delivery_type", "content", "file_id", "sort_order"}

    def test_creates_cart_table(self, db_conn):
        cur = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='cart'"
        )
        assert cur.fetchone() is not None

    def test_cart_table_columns(self, db_conn):
        cur = db_conn.execute("PRAGMA table_info(cart)")
        cols = {row[1] for row in cur.fetchall()}
        assert cols == {"id", "telegram_id", "product_id", "quantity"}

    def test_creates_orders_table(self, db_conn):
        cur = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='orders'"
        )
        assert cur.fetchone() is not None

    def test_orders_table_columns(self, db_conn):
        cur = db_conn.execute("PRAGMA table_info(orders)")
        cols = {row[1] for row in cur.fetchall()}
        assert cols == {"id", "telegram_id", "total", "status", "type"}

    def test_creates_order_items_table(self, db_conn):
        cur = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='order_items'"
        )
        assert cur.fetchone() is not None

    def test_order_items_table_columns(self, db_conn):
        cur = db_conn.execute("PRAGMA table_info(order_items)")
        cols = {row[1] for row in cur.fetchall()}
        assert cols == {"id", "order_id", "product_id", "quantity"}

    def test_creates_payments_table(self, db_conn):
        cur = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='payments'"
        )
        assert cur.fetchone() is not None

    def test_payments_table_columns(self, db_conn):
        cur = db_conn.execute("PRAGMA table_info(payments)")
        cols = {row[1] for row in cur.fetchall()}
        assert cols == {"id", "order_id", "provider", "status"}

    def test_creates_settings_table(self, db_conn):
        cur = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='settings'"
        )
        assert cur.fetchone() is not None

    def test_settings_table_columns(self, db_conn):
        cur = db_conn.execute("PRAGMA table_info(settings)")
        cols = {row[1] for row in cur.fetchall()}
        assert cols == {"key", "value"}

    def test_creates_broadcasts_table(self, db_conn):
        cur = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='broadcasts'"
        )
        assert cur.fetchone() is not None

    def test_broadcasts_table_columns(self, db_conn):
        cur = db_conn.execute("PRAGMA table_info(broadcasts)")
        cols = {row[1] for row in cur.fetchall()}
        assert cols == {"id", "media_type", "file_id", "caption", "sent_at"}

    def test_creates_users_table(self, db_conn):
        cur = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert cur.fetchone() is not None

    def test_users_table_columns(self, db_conn):
        cur = db_conn.execute("PRAGMA table_info(users)")
        cols = {row[1] for row in cur.fetchall()}
        assert cols == {"telegram_id", "username", "joined_at"}

    def test_idempotent(self, tmp_db):
        """Calling init_db twice should not raise."""
        with patch.object(database_mod, "DB_NAME", tmp_db):
            init_db()
            init_db()
