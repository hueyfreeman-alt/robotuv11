import sqlite3
from unittest.mock import patch

import db.database as database_mod
from services.product_service import (
    get_all_products,
    get_product,
    get_products_by_category,
    get_categories,
    add_product,
    update_product,
    delete_product,
    decrease_stock,
)


def _seed(db_path, name="Widget", price=9.99, stock=100, category="gadgets", ptype="physical"):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO products (name, description, price, stock, category, type) VALUES (?, '', ?, ?, ?, ?)",
        (name, price, stock, category, ptype),
    )
    conn.commit()
    pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return pid


class TestGetAllProducts:
    def test_empty(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_all_products() == []

    def test_returns_in_stock_only(self, tmp_db):
        _seed(tmp_db, "A", stock=5)
        _seed(tmp_db, "B", stock=0)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            products = get_all_products()
            assert len(products) == 1
            assert products[0][1] == "A"

    def test_tuple_structure(self, tmp_db):
        _seed(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            pid, name, price, stock, category, ptype = get_all_products()[0]
            assert isinstance(pid, int)
            assert name == "Widget"
            assert price == 9.99
            assert stock == 100


class TestGetProduct:
    def test_existing(self, tmp_db):
        pid = _seed(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            p = get_product(pid)
            assert p is not None
            assert p[1] == "Widget"

    def test_missing(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_product(999) is None


class TestGetProductsByCategory:
    def test_filters_by_category(self, tmp_db):
        _seed(tmp_db, "A", category="cat1")
        _seed(tmp_db, "B", category="cat2")
        with patch.object(database_mod, "DB_NAME", tmp_db):
            rows = get_products_by_category("cat1")
            assert len(rows) == 1
            assert rows[0][1] == "A"

    def test_excludes_out_of_stock(self, tmp_db):
        _seed(tmp_db, "A", category="cat1", stock=0)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_products_by_category("cat1") == []


class TestGetCategories:
    def test_distinct_categories(self, tmp_db):
        _seed(tmp_db, "A", category="X")
        _seed(tmp_db, "B", category="X")
        _seed(tmp_db, "C", category="Y")
        with patch.object(database_mod, "DB_NAME", tmp_db):
            cats = get_categories()
            assert set(cats) == {"X", "Y"}

    def test_excludes_out_of_stock(self, tmp_db):
        _seed(tmp_db, "A", category="Z", stock=0)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_categories() == []


class TestAddProduct:
    def test_returns_id(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            pid = add_product("New", "desc", 5.0, 10, "cat", "physical")
            assert isinstance(pid, int)
            p = get_product(pid)
            assert p[1] == "New"
            assert p[2] == "desc"


class TestUpdateProduct:
    def test_updates_field(self, tmp_db):
        pid = _seed(tmp_db, "Old")
        with patch.object(database_mod, "DB_NAME", tmp_db):
            update_product(pid, name="New", price=1.0)
            p = get_product(pid)
            assert p[1] == "New"
            assert p[3] == 1.0


class TestDeleteProduct:
    def test_removes_product(self, tmp_db):
        pid = _seed(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            delete_product(pid)
            assert get_product(pid) is None


class TestDecreaseStock:
    def test_decreases(self, tmp_db):
        pid = _seed(tmp_db, stock=50)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            decrease_stock(pid, 10)
            p = get_product(pid)
            assert p[4] == 40

    def test_does_not_affect_others(self, tmp_db):
        pid1 = _seed(tmp_db, "A", stock=50)
        pid2 = _seed(tmp_db, "B", stock=99)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            decrease_stock(pid1, 5)
            assert get_product(pid2)[4] == 99
