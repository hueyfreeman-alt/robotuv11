import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_callback(data, user_id=999):
    cb = AsyncMock()
    cb.data = data
    cb.from_user = MagicMock()
    cb.from_user.id = user_id
    cb.message = AsyncMock()
    cb.bot = AsyncMock()
    cb.answer = AsyncMock()
    return cb


def _make_message(text, user_id=999):
    msg = AsyncMock()
    msg.text = text
    msg.from_user = MagicMock()
    msg.from_user.id = user_id
    msg.answer = AsyncMock()
    return msg


def _make_state():
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    state.clear = AsyncMock()
    return state


ADMIN = 999


class TestAdminPanelCallback:
    @pytest.mark.asyncio
    async def test_admin_cb_shows_panel(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import admin_panel_cb
            cb = _make_callback("admin_panel", user_id=ADMIN)
            state = _make_state()
            await admin_panel_cb(cb, state)
            state.clear.assert_called_once()
            cb.message.edit_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_admin_cb_denied(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import admin_panel_cb
            cb = _make_callback("admin_panel", user_id=1)
            state = _make_state()
            await admin_panel_cb(cb, state)
            cb.answer.assert_called_once_with("Access denied")


class TestStats:
    @pytest.mark.asyncio
    async def test_shows_stats(self):
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.get_user_count", return_value=42),
            patch("routers.admin.get_all_products", return_value=[(1, "A", 1, 1, "c", "d")]),
        ):
            from routers.admin import stats
            cb = _make_callback("adm_stats", user_id=ADMIN)
            await stats(cb)
            text = cb.message.edit_text.call_args[0][0]
            assert "42" in text
            assert "1" in text


class TestListProducts:
    @pytest.mark.asyncio
    async def test_no_products(self):
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.get_all_products", return_value=[]),
        ):
            from routers.admin import list_products
            cb = _make_callback("adm_products", user_id=ADMIN)
            await list_products(cb)
            assert "No products" in cb.message.edit_text.call_args[0][0]

    @pytest.mark.asyncio
    async def test_with_products(self):
        products = [(1, "Widget", 10, 5, "cat", "physical")]
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.get_all_products", return_value=products),
        ):
            from routers.admin import list_products
            cb = _make_callback("adm_products", user_id=ADMIN)
            await list_products(cb)
            cb.message.edit_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_denied(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import list_products
            cb = _make_callback("adm_products", user_id=1)
            await list_products(cb)
            cb.answer.assert_called_once_with("Access denied")


class TestViewProduct:
    @pytest.mark.asyncio
    async def test_product_found(self):
        product = (1, "Widget", "desc", 10.0, 5, "cat", "physical")
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.get_product", return_value=product),
            patch("routers.admin.get_delivery_items", return_value=[]),
        ):
            from routers.admin import view_product
            cb = _make_callback("vprod_1", user_id=ADMIN)
            await view_product(cb)
            text = cb.message.edit_text.call_args[0][0]
            assert "Widget" in text

    @pytest.mark.asyncio
    async def test_product_not_found(self):
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.get_product", return_value=None),
        ):
            from routers.admin import view_product
            cb = _make_callback("vprod_999", user_id=ADMIN)
            await view_product(cb)
            cb.answer.assert_called_once_with("Product not found")

    @pytest.mark.asyncio
    async def test_product_with_delivery_items(self):
        product = (1, "Widget", "desc", 10.0, 5, "cat", "digital")
        items = [("text", "key123", None)]
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.get_product", return_value=product),
            patch("routers.admin.get_delivery_items", return_value=items),
        ):
            from routers.admin import view_product
            cb = _make_callback("vprod_1", user_id=ADMIN)
            await view_product(cb)
            text = cb.message.edit_text.call_args[0][0]
            assert "Delivery items" in text


class TestAddProductFlow:
    @pytest.mark.asyncio
    async def test_start(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import add_product_start
            cb = _make_callback("adm_addprod", user_id=ADMIN)
            state = _make_state()
            await add_product_start(cb, state)
            state.set_state.assert_called_once()
            cb.message.edit_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_name_step(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import add_product_name
            msg = _make_message("TestProduct", user_id=ADMIN)
            state = _make_state()
            await add_product_name(msg, state)
            state.update_data.assert_called_once_with(name="TestProduct")

    @pytest.mark.asyncio
    async def test_desc_step(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import add_product_desc
            msg = _make_message("A cool item", user_id=ADMIN)
            state = _make_state()
            await add_product_desc(msg, state)
            state.update_data.assert_called_once_with(description="A cool item")

    @pytest.mark.asyncio
    async def test_desc_skip(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import add_product_desc
            msg = _make_message("-", user_id=ADMIN)
            state = _make_state()
            await add_product_desc(msg, state)
            state.update_data.assert_called_once_with(description="")

    @pytest.mark.asyncio
    async def test_price_step_valid(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import add_product_price
            msg = _make_message("9.99", user_id=ADMIN)
            state = _make_state()
            await add_product_price(msg, state)
            state.update_data.assert_called_once_with(price=9.99)

    @pytest.mark.asyncio
    async def test_price_step_invalid(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import add_product_price
            msg = _make_message("abc", user_id=ADMIN)
            state = _make_state()
            await add_product_price(msg, state)
            assert "Invalid" in msg.answer.call_args[0][0]
            state.update_data.assert_not_called()

    @pytest.mark.asyncio
    async def test_stock_step_valid(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import add_product_stock
            msg = _make_message("50", user_id=ADMIN)
            state = _make_state()
            await add_product_stock(msg, state)
            state.update_data.assert_called_once_with(stock=50)

    @pytest.mark.asyncio
    async def test_stock_step_invalid(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import add_product_stock
            msg = _make_message("abc", user_id=ADMIN)
            state = _make_state()
            await add_product_stock(msg, state)
            assert "Invalid" in msg.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_category_step_creates_product(self):
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.add_product", return_value=7) as mock_add,
        ):
            from routers.admin import add_product_category
            msg = _make_message("Electronics", user_id=ADMIN)
            state = _make_state()
            state.get_data.return_value = {
                "name": "Test",
                "description": "desc",
                "price": 9.99,
                "stock": 10,
            }
            await add_product_category(msg, state)
            mock_add.assert_called_once()
            state.clear.assert_called_once()


class TestDeleteProduct:
    @pytest.mark.asyncio
    async def test_deletes(self):
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.delete_product") as mock_del,
        ):
            from routers.admin import delete_prod
            cb = _make_callback("vdel_5", user_id=ADMIN)
            await delete_prod(cb)
            mock_del.assert_called_once_with(5)
            assert "deleted" in cb.message.edit_text.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_denied(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import delete_prod
            cb = _make_callback("vdel_5", user_id=1)
            await delete_prod(cb)
            cb.answer.assert_called_once_with("Access denied")


class TestDeliveryMenu:
    @pytest.mark.asyncio
    async def test_no_products(self):
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.get_all_products", return_value=[]),
        ):
            from routers.admin import delivery_menu
            cb = _make_callback("adm_delivery", user_id=ADMIN)
            await delivery_menu(cb)
            assert "No products" in cb.message.edit_text.call_args[0][0]

    @pytest.mark.asyncio
    async def test_with_products(self):
        products = [(1, "Widget", 10, 5, "cat", "digital")]
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.get_all_products", return_value=products),
            patch("routers.admin.get_delivery_items", return_value=[]),
        ):
            from routers.admin import delivery_menu
            cb = _make_callback("adm_delivery", user_id=ADMIN)
            await delivery_menu(cb)
            cb.message.edit_text.assert_called_once()


class TestEditProductFlow:
    @pytest.mark.asyncio
    async def test_start(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import edit_product_start
            cb = _make_callback("vedit_3", user_id=ADMIN)
            state = _make_state()
            await edit_product_start(cb, state)
            state.update_data.assert_called_once_with(edit_product_id=3)

    @pytest.mark.asyncio
    async def test_field_selected(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import edit_field_selected
            cb = _make_callback("efield_name", user_id=ADMIN)
            state = _make_state()
            await edit_field_selected(cb, state)
            state.update_data.assert_called_once_with(edit_field="name")

    @pytest.mark.asyncio
    async def test_value_update_text(self):
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.update_product") as mock_update,
        ):
            from routers.admin import edit_product_value
            msg = _make_message("NewName", user_id=ADMIN)
            state = _make_state()
            state.get_data.return_value = {"edit_product_id": 1, "edit_field": "name"}
            await edit_product_value(msg, state)
            mock_update.assert_called_once_with(1, name="NewName")
            state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_value_price_invalid(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import edit_product_value
            msg = _make_message("abc", user_id=ADMIN)
            state = _make_state()
            state.get_data.return_value = {"edit_product_id": 1, "edit_field": "price"}
            await edit_product_value(msg, state)
            assert "Invalid" in msg.answer.call_args[0][0]

    @pytest.mark.asyncio
    async def test_value_stock_invalid(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import edit_product_value
            msg = _make_message("xyz", user_id=ADMIN)
            state = _make_state()
            state.get_data.return_value = {"edit_product_id": 1, "edit_field": "stock"}
            await edit_product_value(msg, state)
            assert "Invalid" in msg.answer.call_args[0][0]


class TestViewDelivery:
    @pytest.mark.asyncio
    async def test_no_items(self):
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.get_delivery_items", return_value=[]),
            patch("routers.admin.get_product", return_value=(1, "Widget", "", 10, 5, "c", "d")),
        ):
            from routers.admin import view_delivery
            cb = _make_callback("vdeliv_1", user_id=ADMIN)
            await view_delivery(cb)
            assert "No delivery items" in cb.message.edit_text.call_args[0][0]

    @pytest.mark.asyncio
    async def test_with_items(self):
        items = [("text", "key123", None), ("photo", None, "fileid")]
        with (
            patch("routers.admin.ADMIN_ID", ADMIN),
            patch("routers.admin.get_delivery_items", return_value=items),
            patch("routers.admin.get_product", return_value=(1, "Widget", "", 10, 5, "c", "d")),
        ):
            from routers.admin import view_delivery
            cb = _make_callback("vdeliv_1", user_id=ADMIN)
            await view_delivery(cb)
            text = cb.message.edit_text.call_args[0][0]
            assert "key123" in text


class TestDeliveryAddMenu:
    @pytest.mark.asyncio
    async def test_shows_type_keyboard(self):
        with patch("routers.admin.ADMIN_ID", ADMIN):
            from routers.admin import delivery_add_menu
            cb = _make_callback("dadd_menu_3", user_id=ADMIN)
            await delivery_add_menu(cb)
            cb.message.edit_text.assert_called_once()
