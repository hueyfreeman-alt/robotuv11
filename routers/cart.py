from aiogram import Router
from aiogram.types import CallbackQuery

from services.cart_service import get_cart, clear_cart
from ui.keyboards import cart_keyboard, back_to_menu

router = Router()


@router.callback_query(lambda c: c.data == "view_cart")
async def view_cart(callback: CallbackQuery):
    items = get_cart(callback.from_user.id)
    if not items:
        await callback.message.edit_text("Cart is empty.", reply_markup=back_to_menu())
        await callback.answer()
        return

    total = sum(price * qty for _, _, price, qty, _ in items)
    lines = []
    for _, name, price, qty, _ in items:
        lines.append(f"  {name} x{qty} — {price * qty:.2f}$")

    text = (
        "<b>🛒 Your Cart</b>\n\n"
        + "\n".join(lines)
        + f"\n\n<b>Total: {total:.2f}$</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=cart_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery):
    clear_cart(callback.from_user.id)
    await callback.message.edit_text("Cart cleared.", reply_markup=back_to_menu())
    await callback.answer()
