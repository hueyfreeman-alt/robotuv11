import pytest
from unittest.mock import AsyncMock

from services.delivery_service import deliver


@pytest.mark.asyncio
class TestDeliver:
    async def test_sends_message_to_user(self):
        bot = AsyncMock()
        items = [("Widget", 9.99, 2), ("Gizmo", 4.50, 1)]
        await deliver(bot, 12345, items)
        bot.send_message.assert_called_once()
        args = bot.send_message.call_args
        assert args[0][0] == 12345

    async def test_message_contains_item_names(self):
        bot = AsyncMock()
        items = [("Widget", 9.99, 2), ("Gizmo", 4.50, 1)]
        await deliver(bot, 12345, items)
        text = bot.send_message.call_args[0][1]
        assert "Widget" in text
        assert "Gizmo" in text

    async def test_message_contains_quantities(self):
        bot = AsyncMock()
        items = [("Widget", 9.99, 3)]
        await deliver(bot, 12345, items)
        text = bot.send_message.call_args[0][1]
        assert "x3" in text

    async def test_empty_items(self):
        bot = AsyncMock()
        await deliver(bot, 12345, [])
        bot.send_message.assert_called_once()
