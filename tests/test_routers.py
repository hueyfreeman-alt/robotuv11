import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import InlineKeyboardMarkup


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_callback(data, user_id=12345):
    cb = AsyncMock()
    cb.data = data
    cb.from_user = MagicMock()
    cb.from_user.id = user_id
    cb.message = AsyncMock()
    cb.bot = AsyncMock()
    cb.answer = AsyncMock()
    return cb


def _make_message(text, user_id=12345):
    msg = AsyncMock()
    msg.text = text
    msg.from_user = MagicMock()
    msg.from_user.id = user_id
    msg.answer = AsyncMock()
    return msg


# ---------------------------------------------------------------------------
# routers/start.py
# ---------------------------------------------------------------------------

class TestStartRouter:
    @pytest.mark.asyncio
    async def test_start_sends_welcome(self):
        from routers.start import start

        msg = _make_message("/start")
        await start(msg)
        msg.answer.assert_called_once()
        args, kwargs = msg.answer.call_args
        assert "Welcome" in args[0]
        assert "reply_markup" in kwargs


# ---------------------------------------------------------------------------
# routers/shop.py
# ---------------------------------------------------------------------------

class TestShopRouter:
    @pytest.mark.asyncio
    async def test_shop_no_products(self):
        with patch("routers.shop.get_all_products", return_value=[]):
            from routers.shop import shop

            cb = _make_callback("shop")
            await shop(cb)
            cb.message.answer.assert_called_once()
            assert "No products" in cb.message.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_shop_lists_products(self):
        products = [
            (1, "Widget", 9.99, 10, "gadgets", "physical"),
            (2, "E-Book", 4.99, 99, "digital", "digital"),
        ]
        with patch("routers.shop.get_all_products", return_value=products):
            from routers.shop import shop

            cb = _make_callback("shop")
            await shop(cb)
            assert cb.message.answer.call_count == 2
            cb.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_to_cart_callback(self):
        with patch("routers.shop.add_to_cart") as mock_add:
            from routers.shop import add

            cb = _make_callback("add_42", user_id=111)
            await add(cb)
            mock_add.assert_called_once_with(111, 42, 1)
            cb.answer.assert_called_once()


# ---------------------------------------------------------------------------
# routers/cart.py
# ---------------------------------------------------------------------------

class TestCartRouter:
    @pytest.mark.asyncio
    async def test_cart_empty(self):
        with patch("routers.cart.get_cart", return_value=[]):
            from routers.cart import cart

            cb = _make_callback("cart")
            await cart(cb)
            assert "empty" in cb.message.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_cart_with_items(self):
        items = [("Widget", 10.0, 2), ("Gizmo", 5.0, 1)]
        with patch("routers.cart.get_cart", return_value=items):
            from routers.cart import cart

            cb = _make_callback("cart")
            await cart(cb)
            text = cb.message.answer.call_args[0][0]
            assert "Widget" in text
            assert "25.0" in text  # total

    @pytest.mark.asyncio
    async def test_clear_cart(self):
        with patch("routers.cart.clear_cart") as mock_clear:
            from routers.cart import clear

            cb = _make_callback("clear_cart", user_id=555)
            await clear(cb)
            mock_clear.assert_called_once_with(555)
            cb.answer.assert_called_once()


# ---------------------------------------------------------------------------
# routers/checkout.py
# ---------------------------------------------------------------------------

class TestCheckoutRouter:
    @pytest.mark.asyncio
    async def test_checkout_empty_cart(self):
        with patch("routers.checkout.get_cart", return_value=[]):
            from routers.checkout import checkout

            cb = _make_callback("checkout")
            await checkout(cb)
            assert "empty" in cb.message.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_checkout_full_flow(self):
        items = [("Widget", 10.0, 2)]
        raw = [(1, 2)]
        with (
            patch("routers.checkout.get_cart", return_value=items),
            patch("routers.checkout.get_cart_raw", return_value=raw),
            patch("routers.checkout.create_order", return_value=1) as mock_order,
            patch("routers.checkout.add_order_items") as mock_items,
            patch("routers.checkout.decrease_stock") as mock_stock,
            patch("routers.checkout.create_payment") as mock_pay,
            patch("routers.checkout.clear_cart") as mock_clear,
            patch("routers.checkout.deliver", new_callable=AsyncMock) as mock_deliver,
        ):
            from routers.checkout import checkout

            cb = _make_callback("checkout", user_id=777)
            await checkout(cb)

            mock_order.assert_called_once_with(777, 20.0, "mixed")
            mock_items.assert_called_once_with(1, raw)
            mock_stock.assert_called_once_with(1, 2)
            mock_pay.assert_called_once_with(1, 20.0)
            mock_clear.assert_called_once_with(777)
            mock_deliver.assert_called_once()

            text = cb.message.answer.call_args[0][0]
            assert "ORDER #1" in text
            assert "20.0" in text


# ---------------------------------------------------------------------------
# routers/admin.py
# ---------------------------------------------------------------------------

class TestAdminRouter:
    @pytest.mark.asyncio
    async def test_non_admin_ignored(self):
        with patch("routers.admin.ADMIN_ID", 999):
            from routers.admin import set_status

            msg = _make_message("/set|1|shipped", user_id=123)
            await set_status(msg)
            msg.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_admin_set_status(self):
        with patch("routers.admin.ADMIN_ID", 999):
            from routers.admin import set_status

            msg = _make_message("/set|42|shipped", user_id=999)
            await set_status(msg)
            msg.answer.assert_called_once()
            assert "42" in msg.answer.call_args[0][0]
            assert "shipped" in msg.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_admin_bad_format(self):
        with patch("routers.admin.ADMIN_ID", 999):
            from routers.admin import set_status

            msg = _make_message("/set_bad_format", user_id=999)
            await set_status(msg)
            msg.answer.assert_called_once()
            assert "Format" in msg.answer.call_args[0][0]
