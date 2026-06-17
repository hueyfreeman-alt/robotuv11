from aiogram import Router
from aiogram.types import CallbackQuery

from services.cart_service import get_cart, get_cart_raw, clear_cart
from services.order_service import create_order, add_order_items
from services.payment_service import create_payment
from ui.keyboards import back_to_menu

router = Router()


@router.callback_query(lambda c: c.data == "checkout")
async def checkout(callback: CallbackQuery):
    user_id = callback.from_user.id
    items = get_cart(user_id)

    if not items:
        await callback.message.edit_text(
            "Cart is empty.",
            reply_markup=back_to_menu(),
        )
        await callback.answer()
        return

    total = sum(price * qty for _, price, qty in items)

    order_id = create_order(user_id, total, "mixed")

    raw = get_cart_raw(user_id)
    add_order_items(order_id, raw)

    create_payment(order_id, total)
    clear_cart(user_id)

    await callback.message.answer(
        f"<b>Order #{order_id} created</b>\n"
        f"Total: {total}$\n\n"
        "Payment status: pending.\n"
        "Your digital items will be delivered after payment confirmation.",
        parse_mode="HTML",
        reply_markup=back_to_menu(),
    )
    await callback.answer()
