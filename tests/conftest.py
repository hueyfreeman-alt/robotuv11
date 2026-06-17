import os
import sqlite3
import pytest
from unittest.mock import patch

import db.database as database_mod


@pytest.fixture()
def tmp_db(tmp_path):
    """Provide an isolated SQLite database for each test."""
    db_path = str(tmp_path / "test_shop.db")
    with patch.object(database_mod, "DB_NAME", db_path):
        database_mod.init_db()
        yield db_path


@pytest.fixture()
def db_conn(tmp_db):
    """Return a connection to the test database."""
    conn = sqlite3.connect(tmp_db)
    yield conn
    conn.close()
