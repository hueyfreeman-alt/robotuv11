from unittest.mock import patch

import db.database as database_mod
from services.settings_service import get_setting, set_setting, delete_setting


class TestGetSetting:
    def test_returns_default_when_missing(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_setting("nonexistent") is None

    def test_returns_custom_default(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_setting("nonexistent", "fallback") == "fallback"

    def test_returns_stored_value(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            set_setting("color", "blue")
            assert get_setting("color") == "blue"


class TestSetSetting:
    def test_insert_new(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            set_setting("key1", "val1")
            assert get_setting("key1") == "val1"

    def test_upsert_existing(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            set_setting("key1", "old")
            set_setting("key1", "new")
            assert get_setting("key1") == "new"


class TestDeleteSetting:
    def test_removes_setting(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            set_setting("temp", "val")
            delete_setting("temp")
            assert get_setting("temp") is None

    def test_noop_if_missing(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            delete_setting("nonexistent")  # should not raise
