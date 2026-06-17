import pytest
from unittest.mock import AsyncMock, MagicMock, patch


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


def _make_message(text, user_id=12345, username="testuser"):
    msg = AsyncMock()
    msg.text = text
    msg.from_user = MagicMock()
    msg.from_user.id = user_id
    msg.from_user.username = username
    msg.answer = AsyncMock()
    msg.answer_animation = AsyncMock()
    msg.answer_video = AsyncMock()
    msg.answer_photo = AsyncMock()
    return msg


# ---------------------------------------------------------------------------
# routers/start.py
# ---------------------------------------------------------------------------

class TestStartRouter:
    @pytest.mark.asyncio
    async def test_start_sends_welcome(self):
        with (
            patch("routers.start.register_user"),
            patch("routers.start.get_setting", return_value=None),
        ):
            from routers.start import start
            msg = _make_message("/start")
            await start(msg)
            msg.answer.assert_called_once()
            assert "Welcome" in msg.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_start_registers_user(self):
        with (
            patch("routers.start.register_user") as mock_reg,
            patch("routers.start.get_setting", return_value=None),
        ):
            from routers.start import start
            msg = _make_message("/start", user_id=42, username="alice")
            await start(msg)
            mock_reg.assert_called_once_with(42, "alice")

    @pytest.mark.asyncio
    async def test_back_menu(self):
        from routers.start import back_menu
        cb = _make_callback("back_menu")
        await back_menu(cb)
        cb.message.edit_text.assert_called_once()
        cb.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_help_handler(self):
        from routers.start import help_handler
        cb = _make_callback("help")
        await help_handler(cb)
        cb.message.edit_text.assert_called_once()
        text = cb.message.edit_text.call_args[0][0]
        assert "Shop" in text
        assert "Cart" in text

    @pytest.mark.asyncio
    async def test_start_with_promo_photo(self):
        def fake_setting(key, default=None):
            return {"promo_type": "photo", "promo_file_id": "abc", "promo_caption": "Sale!"}.get(key, default)

        with (
            patch("routers.start.register_user"),
            patch("routers.start.get_setting", side_effect=fake_setting),
        ):
            from routers.start import start
            msg = _make_message("/start")
            await start(msg)
            msg.answer_photo.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_with_promo_video(self):
        def fake_setting(key, default=None):
            return {"promo_type": "video", "promo_file_id": "vid1", "promo_caption": ""}.get(key, default)

        with (
            patch("routers.start.register_user"),
            patch("routers.start.get_setting", side_effect=fake_setting),
        ):
            from routers.start import start
            msg = _make_message("/start")
            await start(msg)
            msg.answer_video.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_with_promo_gif(self):
        def fake_setting(key, default=None):
            return {"promo_type": "gif", "promo_file_id": "gif1", "promo_caption": ""}.get(key, default)

        with (
            patch("routers.start.register_user"),
            patch("routers.start.get_setting", side_effect=fake_setting),
        ):
            from routers.start import start
            msg = _make_message("/start")
            await start(msg)
            msg.answer_animation.assert_called_once()


# ---------------------------------------------------------------------------
# routers/shop.py
# ---------------------------------------------------------------------------

class TestShopRouter:
    @pytest.mark.asyncio
    async def test_shop_no_categories(self):
        with patch("routers.shop.get_categories", return_value=[]):
            from routers.shop import shop
            cb = _make_callback("shop")
            await shop(cb)
            cb.message.edit_text.assert_called_once()
            assert "No products" in cb.message.edit_text.call_args[0][0]

    @pytest.mark.asyncio
    async def test_shop_single_category_shows_products(self):
        products = [(1, "Widget", 9.99, 10, "gadgets", "physical")]
        with (
            patch("routers.shop.get_categories", return_value=["gadgets"]),
            patch("routers.shop.get_products_by_category", return_value=products),
        ):
            from routers.shop import shop
            cb = _make_callback("shop")
            await shop(cb)
            cb.message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_shop_multiple_categories_shows_keyboard(self):
        with patch("routers.shop.get_categories", return_value=["A", "B"]):
            from routers.shop import shop
            cb = _make_callback("shop")
            await shop(cb)
            cb.message.edit_text.assert_called_once()
            assert "category" in cb.message.edit_text.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_add_to_cart_callback(self):
        with patch("routers.shop.add_to_cart") as mock_add:
            from routers.shop import add
            cb = _make_callback("add_42", user_id=111)
            await add(cb)
            mock_add.assert_called_once_with(111, 42, 1)
            cb.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_category_handler(self):
        products = [(1, "Widget", 9.99, 10, "gadgets", "physical")]
        with patch("routers.shop.get_products_by_category", return_value=products):
            from routers.shop import category
            cb = _make_callback("cat_gadgets")
            await category(cb)
            cb.message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_products_empty(self):
        with patch("routers.shop.get_products_by_category", return_value=[]):
            from routers.shop import category
            cb = _make_callback("cat_empty")
            await category(cb)
            assert "No products" in cb.message.edit_text.call_args[0][0]


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
            assert "empty" in cb.message.edit_text.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_cart_with_items(self):
        items = [("Widget", 10.0, 2), ("Gizmo", 5.0, 1)]
        with patch("routers.cart.get_cart", return_value=items):
            from routers.cart import cart
            cb = _make_callback("cart")
            await cart(cb)
            text = cb.message.edit_text.call_args[0][0]
            assert "Widget" in text
            assert "25.0" in text  # total

    @pytest.mark.asyncio
    async def test_clear_cart(self):
        with patch("routers.cart.clear_cart") as mock_clear:
            from routers.cart import clear
            cb = _make_callback("clear_cart", user_id=555)
            await clear(cb)
            mock_clear.assert_called_once_with(555)


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
            assert "empty" in cb.message.edit_text.call_args[0][0].lower()

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
            patch("routers.checkout.deliver_by_product_ids", new_callable=AsyncMock) as mock_deliver,
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
            assert "Order #1" in text
            assert "20.0" in text


# ---------------------------------------------------------------------------
# routers/admin.py
# ---------------------------------------------------------------------------

class TestAdminRouter:
    @pytest.mark.asyncio
    async def test_non_admin_ignored(self):
        with patch("routers.admin.ADMIN_ID", 999):
            from routers.admin import admin_panel
            msg = _make_message("/admin", user_id=123)
            await admin_panel(msg)
            msg.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_admin_panel_shows_menu(self):
        with patch("routers.admin.ADMIN_ID", 999):
            from routers.admin import admin_panel
            msg = _make_message("/admin", user_id=999)
            await admin_panel(msg)
            msg.answer.assert_called_once()
            assert "Admin" in msg.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_is_admin_helper(self):
        with patch("routers.admin.ADMIN_ID", 42):
            from routers.admin import is_admin
            assert is_admin(42) is True
            assert is_admin(99) is False

    @pytest.mark.asyncio
    async def test_stats_non_admin(self):
        with (
            patch("routers.admin.ADMIN_ID", 999),
            patch("routers.admin.is_admin", return_value=False),
        ):
            from routers.admin import stats
            cb = _make_callback("adm_stats", user_id=123)
            await stats(cb)
            cb.answer.assert_called_once_with("Access denied")
