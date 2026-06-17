from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ui.keyboards import (
    main_menu,
    back_to_menu,
    category_keyboard,
    product_actions,
    cart_keyboard,
    admin_menu,
    vendor_product_actions,
    delivery_type_keyboard,
    broadcast_type_keyboard,
    confirm_keyboard,
)


class TestMainMenu:
    def test_returns_inline_keyboard_markup(self):
        kb = main_menu()
        assert isinstance(kb, InlineKeyboardMarkup)

    def test_has_three_rows(self):
        kb = main_menu()
        assert len(kb.inline_keyboard) == 3

    def test_shop_button(self):
        btn = main_menu().inline_keyboard[0][0]
        assert btn.callback_data == "shop"

    def test_cart_button(self):
        btn = main_menu().inline_keyboard[1][0]
        assert btn.callback_data == "cart"

    def test_help_button(self):
        btn = main_menu().inline_keyboard[2][0]
        assert btn.callback_data == "help"


class TestBackToMenu:
    def test_single_back_button(self):
        kb = back_to_menu()
        assert len(kb.inline_keyboard) == 1
        assert kb.inline_keyboard[0][0].callback_data == "back_menu"


class TestCategoryKeyboard:
    def test_one_button_per_category_plus_back(self):
        kb = category_keyboard(["Electronics", "Books"])
        assert len(kb.inline_keyboard) == 3
        assert kb.inline_keyboard[0][0].callback_data == "cat_Electronics"
        assert kb.inline_keyboard[1][0].callback_data == "cat_Books"
        assert kb.inline_keyboard[2][0].callback_data == "back_menu"

    def test_empty_categories(self):
        kb = category_keyboard([])
        assert len(kb.inline_keyboard) == 1  # just back


class TestProductActions:
    def test_add_and_back_buttons(self):
        kb = product_actions(42)
        assert len(kb.inline_keyboard) == 2
        assert kb.inline_keyboard[0][0].callback_data == "add_42"
        assert kb.inline_keyboard[1][0].callback_data == "shop"


class TestCartKeyboard:
    def test_checkout_clear_back(self):
        kb = cart_keyboard()
        assert len(kb.inline_keyboard) == 3
        data = [row[0].callback_data for row in kb.inline_keyboard]
        assert "checkout" in data
        assert "clear_cart" in data
        assert "back_menu" in data


class TestAdminMenu:
    def test_has_expected_buttons(self):
        kb = admin_menu()
        data = [row[0].callback_data for row in kb.inline_keyboard]
        assert "adm_products" in data
        assert "adm_delivery" in data
        assert "adm_broadcast" in data
        assert "adm_stats" in data


class TestVendorProductActions:
    def test_buttons_for_product(self):
        kb = vendor_product_actions(7)
        data = [row[0].callback_data for row in kb.inline_keyboard]
        assert "vedit_7" in data
        assert "vdeliv_7" in data
        assert "vdel_7" in data
        assert "adm_products" in data


class TestDeliveryTypeKeyboard:
    def test_delivery_types(self):
        kb = delivery_type_keyboard(5)
        data = [row[0].callback_data for row in kb.inline_keyboard]
        assert "dadd_text_5" in data
        assert "dadd_photo_5" in data
        assert "dadd_video_5" in data
        assert "dadd_file_5" in data
        assert "dadd_coords_5" in data


class TestBroadcastTypeKeyboard:
    def test_photo_and_video(self):
        kb = broadcast_type_keyboard()
        data = [row[0].callback_data for row in kb.inline_keyboard]
        assert "bc_photo" in data
        assert "bc_video" in data


class TestConfirmKeyboard:
    def test_confirm_cancel(self):
        kb = confirm_keyboard("delete")
        buttons = kb.inline_keyboard[0]
        assert len(buttons) == 2
        assert buttons[0].callback_data == "confirm_delete"
        assert buttons[1].callback_data == "cancel_delete"
