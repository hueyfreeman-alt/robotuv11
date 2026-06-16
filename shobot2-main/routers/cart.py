from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.cart_service import get_cart, clear_cart

router = Router()


@router.callback_query(lambda c: c.data == "cart")
async def cart(callback: CallbackQuery):
    items = get_cart(callback.from_user.id)

    if not items:
        await callback.message.answer("🛒 Cart empty")
        return

    total = 0
    text = "🛒 CART:\n\n"

    for name, price, qty in items:
        total += price * qty
        text += f"{name} x{qty} = {price * qty}$\n"

    text += f"\n💰 TOTAL: {total}$"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Checkout", callback_data="checkout")],
        [InlineKeyboardButton(text="🧹 Clear", callback_data="clear_cart")]
    ])

    await callback.message.answer(text, reply_markup=kb)


@router.callback_query(lambda c: c.data == "clear_cart")
async def clear(callback: CallbackQuery):
    clear_cart(callback.from_user.id)
    await callback.answer("Cleared 🧹")
