from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ui.keyboards import main_menu


class TestMainMenu:
    def test_returns_inline_keyboard_markup(self):
        kb = main_menu()
        assert isinstance(kb, InlineKeyboardMarkup)

    def test_has_two_rows(self):
        kb = main_menu()
        assert len(kb.inline_keyboard) == 2

    def test_shop_button(self):
        kb = main_menu()
        btn = kb.inline_keyboard[0][0]
        assert isinstance(btn, InlineKeyboardButton)
        assert btn.callback_data == "shop"
        assert "Shop" in btn.text

    def test_cart_button(self):
        kb = main_menu()
        btn = kb.inline_keyboard[1][0]
        assert isinstance(btn, InlineKeyboardButton)
        assert btn.callback_data == "cart"
        assert "Cart" in btn.text
