from aiogram import Router
from aiogram.types import CallbackQuery

from services.cart_service import get_cart, get_cart_raw, clear_cart
from services.order_service import create_order, add_order_items
from services.product_service import decrease_stock
from services.payment_service import create_payment
from services.delivery_service import deliver

router = Router()


@router.callback_query(lambda c: c.data == "checkout")
async def checkout(callback: CallbackQuery):
    user_id = callback.from_user.id

    items = get_cart(user_id)

    if not items:
        await callback.message.answer("Cart empty")
        return

    total = sum(price * qty for _, price, qty in items)

    order_id = create_order(user_id, total, "mixed")

    raw = get_cart_raw(user_id)
    add_order_items(order_id, raw)

    for pid, qty in raw:
        decrease_stock(pid, qty)

    create_payment(order_id, total)

    clear_cart(user_id)

    await deliver(callback.bot, user_id, items)

    await callback.message.answer(
        f"✅ ORDER #{order_id}\n💰 {total}$"
    )

    await callback.answer()