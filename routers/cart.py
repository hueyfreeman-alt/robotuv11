import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from services.cart_service import get_cart, clear_cart
from ui.keyboards import cart_keyboard, back_to_menu

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(lambda c: c.data == "cart")
async def cart(callback: CallbackQuery):
    items = get_cart(callback.from_user.id)

    if not items:
        await callback.message.edit_text(
            "Your cart is empty.",
            reply_markup=back_to_menu(),
        )
        await callback.answer()
        return

    total = 0
    lines = []
    for name, price, qty in items:
        subtotal = price * qty
        total += subtotal
        lines.append(f"  {name} x{qty} — {subtotal}$")

    text = (
        "<b>🛒 Your Cart</b>\n\n"
        + "\n".join(lines)
        + f"\n\n<b>Total: {total}$</b>"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=cart_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "clear_cart")
async def clear(callback: CallbackQuery):
    try:
        clear_cart(callback.from_user.id)
        await callback.message.edit_text(
            "Cart cleared.",
            reply_markup=back_to_menu(),
        )
        await callback.answer()
    except Exception as e:
        logger.error("Failed to clear cart for user %d: %s", callback.from_user.id, e)
        await callback.answer("❌ Failed to clear cart")
