import sqlite3
from unittest.mock import patch

import db.database as database_mod
from services.cart_service import add_to_cart, get_cart, get_cart_raw, clear_cart


USER_ID = 12345


def _seed_product(db_path, name="Widget", price=9.99, stock=50):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO products (name, price, stock, category, type) VALUES (?, ?, ?, ?, ?)",
        (name, price, stock, "general", "physical"),
    )
    conn.commit()
    pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return pid


class TestAddToCart:
    def test_add_new_item(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_to_cart(USER_ID, pid, 2)
            raw = get_cart_raw(USER_ID)
            assert len(raw) == 1
            assert raw[0] == (pid, 2)

    def test_add_existing_item_increments_quantity(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_to_cart(USER_ID, pid, 1)
            add_to_cart(USER_ID, pid, 3)
            raw = get_cart_raw(USER_ID)
            assert len(raw) == 1
            assert raw[0] == (pid, 4)

    def test_add_different_products(self, tmp_db):
        pid1 = _seed_product(tmp_db, "A", 1.0)
        pid2 = _seed_product(tmp_db, "B", 2.0)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_to_cart(USER_ID, pid1, 1)
            add_to_cart(USER_ID, pid2, 2)
            raw = get_cart_raw(USER_ID)
            assert len(raw) == 2


class TestGetCart:
    def test_empty_cart(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_cart(USER_ID) == []

    def test_returns_name_price_qty(self, tmp_db):
        pid = _seed_product(tmp_db, "Gizmo", 5.50)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_to_cart(USER_ID, pid, 3)
            items = get_cart(USER_ID)
            assert len(items) == 1
            name, price, qty = items[0]
            assert name == "Gizmo"
            assert price == 5.50
            assert qty == 3

    def test_isolates_users(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_to_cart(USER_ID, pid, 1)
            add_to_cart(99999, pid, 5)
            assert len(get_cart(USER_ID)) == 1
            assert get_cart(USER_ID)[0][2] == 1


class TestGetCartRaw:
    def test_returns_product_id_and_quantity(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_to_cart(USER_ID, pid, 7)
            raw = get_cart_raw(USER_ID)
            assert raw == [(pid, 7)]


class TestClearCart:
    def test_clears_all_items(self, tmp_db):
        pid1 = _seed_product(tmp_db, "A")
        pid2 = _seed_product(tmp_db, "B")
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_to_cart(USER_ID, pid1, 1)
            add_to_cart(USER_ID, pid2, 2)
            clear_cart(USER_ID)
            assert get_cart(USER_ID) == []
            assert get_cart_raw(USER_ID) == []

    def test_does_not_clear_other_users(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_to_cart(USER_ID, pid, 1)
            add_to_cart(99999, pid, 3)
            clear_cart(USER_ID)
            assert get_cart_raw(USER_ID) == []
            assert len(get_cart_raw(99999)) == 1
