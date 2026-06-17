from unittest.mock import patch

import db.database as database_mod
from services.user_service import register_user, get_all_users, get_user_count


class TestRegisterUser:
    def test_registers_new_user(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            register_user(111, "alice")
            assert get_user_count() == 1

    def test_ignores_duplicate(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            register_user(111, "alice")
            register_user(111, "alice")
            assert get_user_count() == 1

    def test_multiple_users(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            register_user(111, "alice")
            register_user(222, "bob")
            assert get_user_count() == 2


class TestGetAllUsers:
    def test_returns_telegram_ids(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            register_user(111, "a")
            register_user(222, "b")
            ids = get_all_users()
            assert set(ids) == {111, 222}

    def test_empty(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_all_users() == []


class TestGetUserCount:
    def test_zero(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_user_count() == 0

    def test_counts_correctly(self, tmp_db):
        with patch.object(database_mod, "DB_NAME", tmp_db):
            register_user(1, "")
            register_user(2, "")
            register_user(3, "")
            assert get_user_count() == 3
