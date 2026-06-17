import sqlite3
from unittest.mock import patch

import db.database as database_mod
from services.order_service import create_order, add_order_items


USER_ID = 12345


class TestCreateOrder:
    def test_returns_order_id(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            oid = create_order(USER_ID, 25.50, "physical")
            assert isinstance(oid, int)
            assert oid >= 1

    def test_persists_order(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            oid = create_order(USER_ID, 25.50, "physical")
        conn = sqlite3.connect(tmp_db)
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
        conn.close()
        assert row is not None
        _, tid, total, status, otype = row
        assert tid == USER_ID
        assert total == 25.50
        assert status == "pending"
        assert otype == "physical"

    def test_sequential_ids(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            id1 = create_order(USER_ID, 10, "a")
            id2 = create_order(USER_ID, 20, "b")
            assert id2 == id1 + 1


class TestAddOrderItems:
    def test_inserts_items(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            oid = create_order(USER_ID, 50, "mixed")
            add_order_items(oid, [(1, 2), (3, 4)])
        conn = sqlite3.connect(tmp_db)
        rows = conn.execute(
            "SELECT order_id, product_id, quantity FROM order_items WHERE order_id = ?",
            (oid,),
        ).fetchall()
        conn.close()
        assert len(rows) == 2
        assert (oid, 1, 2) in rows
        assert (oid, 3, 4) in rows

    def test_empty_items(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            oid = create_order(USER_ID, 0, "empty")
            add_order_items(oid, [])
        conn = sqlite3.connect(tmp_db)
        rows = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (oid,)
        ).fetchall()
        conn.close()
        assert rows == []
