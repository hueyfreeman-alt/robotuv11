import sqlite3
import pytest
from unittest.mock import AsyncMock, patch

import db.database as database_mod
from services.delivery_service import (
    get_delivery_items,
    add_delivery_item,
    clear_delivery_items,
    delete_delivery_item,
    deliver_by_product_ids,
)


def _seed_product(db_path, name="Widget"):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO products (name, description, price, stock, category, type) VALUES (?, '', 10, 10, 'cat', 'digital')",
        (name,),
    )
    pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()
    return pid


class TestGetDeliveryItems:
    def test_empty(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            assert get_delivery_items(pid) == []

    def test_returns_items_sorted(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "text", "First")
            add_delivery_item(pid, "photo", "Second", file_id="abc")
            items = get_delivery_items(pid)
            assert len(items) == 2
            assert items[0][0] == "text"
            assert items[0][1] == "First"
            assert items[1][0] == "photo"
            assert items[1][2] == "abc"


class TestAddDeliveryItem:
    def test_auto_increments_sort_order(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "text", "A")
            add_delivery_item(pid, "text", "B")
        conn = sqlite3.connect(tmp_db)
        rows = conn.execute(
            "SELECT sort_order FROM product_delivery WHERE product_id = ? ORDER BY sort_order",
            (pid,),
        ).fetchall()
        conn.close()
        assert rows[0][0] == 1
        assert rows[1][0] == 2


class TestClearDeliveryItems:
    def test_removes_all(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "text", "A")
            add_delivery_item(pid, "text", "B")
            clear_delivery_items(pid)
            assert get_delivery_items(pid) == []


class TestDeleteDeliveryItem:
    def test_removes_single(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "text", "A")
            add_delivery_item(pid, "text", "B")
        conn = sqlite3.connect(tmp_db)
        item_id = conn.execute("SELECT id FROM product_delivery LIMIT 1").fetchone()[0]
        conn.close()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            delete_delivery_item(item_id)
            assert len(get_delivery_items(pid)) == 1


@pytest.mark.asyncio
class TestDeliverByProductIds:
    async def test_sends_text_delivery(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "text", "Your key: ABC123")

        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid])
        assert bot.send_message.call_count >= 2  # header + content

    async def test_no_delivery_items_no_message(self, tmp_db):
        pid = _seed_product(tmp_db)
        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid])
        bot.send_message.assert_not_called()

    async def test_sends_photo_with_file_id(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "photo", "caption", file_id="photo123")

        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid])
        bot.send_photo.assert_called_once()

    async def test_sends_video_with_file_id(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "video", "cap", file_id="vid1")

        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid])
        bot.send_video.assert_called_once()

    async def test_sends_file_with_file_id(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "file", "readme", file_id="doc1")

        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid])
        bot.send_document.assert_called_once()

    async def test_sends_coordinates(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "coordinates", "51.5, -0.1")

        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid])
        bot.send_location.assert_called_once()

    async def test_photo_without_file_id_sends_text(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "photo", "see attached")

        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid])
        bot.send_photo.assert_not_called()
        assert bot.send_message.call_count >= 2

    async def test_video_without_file_id_sends_text(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "video", "watch here")

        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid])
        bot.send_video.assert_not_called()

    async def test_file_without_file_id_sends_text(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "file", "download link")

        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid])
        bot.send_document.assert_not_called()

    async def test_invalid_coordinates_sends_text(self, tmp_db):
        pid = _seed_product(tmp_db)
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid, "coordinates", "bad_data")

        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid])
        bot.send_location.assert_not_called()

    async def test_multiple_products(self, tmp_db):
        pid1 = _seed_product(tmp_db, "A")
        pid2 = _seed_product(tmp_db, "B")
        with patch.object(database_mod, "DB_NAME", tmp_db):
            add_delivery_item(pid1, "text", "key1")
            add_delivery_item(pid2, "text", "key2")

        bot = AsyncMock()
        with patch.object(database_mod, "DB_NAME", tmp_db):
            await deliver_by_product_ids(bot, 12345, [pid1, pid2])
        assert bot.send_message.call_count >= 4  # 2 headers + 2 content
