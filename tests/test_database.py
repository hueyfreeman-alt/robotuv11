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
        assert cols == {"id", "name", "price", "stock", "category", "type"}

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

    def test_idempotent(self, tmp_db):
        """Calling init_db twice should not raise."""
        with patch.object(database_mod, "DB_NAME", tmp_db):
            init_db()
            init_db()
