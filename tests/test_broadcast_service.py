import sqlite3
from unittest.mock import patch

import db.database as database_mod
from services.broadcast_service import save_broadcast, get_broadcasts


class TestSaveBroadcast:
    def test_inserts_broadcast(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            save_broadcast("photo", "file123", "Hello!")
        conn = sqlite3.connect(tmp_db)
        row = conn.execute("SELECT media_type, file_id, caption FROM broadcasts").fetchone()
        conn.close()
        assert row == ("photo", "file123", "Hello!")

    def test_default_caption(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            save_broadcast("video", "vid1")
        conn = sqlite3.connect(tmp_db)
        row = conn.execute("SELECT caption FROM broadcasts").fetchone()
        conn.close()
        assert row[0] == ""


class TestGetBroadcasts:
    def test_empty(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_broadcasts() == []

    def test_returns_latest_first(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            save_broadcast("photo", "f1", "first")
            save_broadcast("video", "f2", "second")
            rows = get_broadcasts()
            assert len(rows) == 2
            assert rows[0][3] == "second"
            assert rows[1][3] == "first"

    def test_respects_limit(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            for i in range(5):
                save_broadcast("photo", f"f{i}", f"cap{i}")
            assert len(get_broadcasts(limit=3)) == 3
