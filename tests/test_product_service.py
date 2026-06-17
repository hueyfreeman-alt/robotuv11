import sqlite3
from unittest.mock import patch

import db.database as database_mod
from services.product_service import get_all_products, decrease_stock


def _seed_products(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO products (name, price, stock, category, type) VALUES (?, ?, ?, ?, ?)",
        ("Widget", 9.99, 100, "gadgets", "physical"),
    )
    conn.execute(
        "INSERT INTO products (name, price, stock, category, type) VALUES (?, ?, ?, ?, ?)",
        ("E-Book", 4.99, 999, "digital", "digital"),
    )
    conn.commit()
    conn.close()


class TestGetAllProducts:
    def test_returns_empty_when_no_products(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_all_products() == []

    def test_returns_all_products(self, tmp_db):
        _seed_products(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            products = get_all_products()
            assert len(products) == 2

    def test_product_tuple_structure(self, tmp_db):
        _seed_products(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            pid, name, price, stock, category, ptype = get_all_products()[0]
            assert isinstance(pid, int)
            assert name == "Widget"
            assert price == 9.99
            assert stock == 100
            assert category == "gadgets"
            assert ptype == "physical"


class TestDecreaseStock:
    def test_decreases_stock(self, tmp_db):
        _seed_products(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            decrease_stock(1, 10)
            products = get_all_products()
            assert products[0][3] == 90

    def test_decrease_to_zero(self, tmp_db):
        _seed_products(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            decrease_stock(1, 100)
            products = get_all_products()
            assert products[0][3] == 0

    def test_does_not_affect_other_products(self, tmp_db):
        _seed_products(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            decrease_stock(1, 5)
            products = get_all_products()
            assert products[1][3] == 999
