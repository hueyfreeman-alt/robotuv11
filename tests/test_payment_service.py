import sqlite3
from unittest.mock import patch

import db.database as database_mod
from services.payment_service import create_payment
from services.order_service import create_order


USER_ID = 12345


class TestCreatePayment:
    def test_inserts_payment(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            oid = create_order(USER_ID, 30.0, "physical")
            create_payment(oid, 30.0)
        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT order_id, provider, status FROM payments WHERE order_id = ?",
            (oid,),
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == oid
        assert row[1] == "internal"
        assert row[2] == "paid"

    def test_multiple_payments(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            oid1 = create_order(USER_ID, 10.0, "a")
            oid2 = create_order(USER_ID, 20.0, "b")
            create_payment(oid1, 10.0)
            create_payment(oid2, 20.0)
        conn = sqlite3.connect(tmp_db)
        rows = conn.execute("SELECT * FROM payments").fetchall()
        conn.close()
        assert len(rows) == 2
