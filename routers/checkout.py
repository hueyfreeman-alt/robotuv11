from aiogram import Router
from aiogram.types import CallbackQuery

from services.cart_service import (
    get_cart, get_cart_raw, clear_cart, compute_cart_total,
)
from services.order_service import create_order, add_order_items
from services.product_service import decrease_stock
from services.payment_service import create_payment
from services.delivery_service import deliver_by_product_ids
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

    total = compute_cart_total(items)

    order_id = create_order(user_id, total, "mixed")

    raw = get_cart_raw(user_id)
    add_order_items(order_id, raw)

    product_ids = []
    for pid, qty in raw:
        decrease_stock(pid, qty)
        product_ids.append(pid)

    create_payment(order_id, total)
    clear_cart(user_id)

    # Deliver digital content
    await deliver_by_product_ids(callback.bot, user_id, product_ids)

    await callback.message.answer(
        f"<b>Order #{order_id} confirmed</b>\n"
        f"Total: {total}$\n\n"
        "Your digital items have been delivered above.",
        parse_mode="HTML",
        reply_markup=back_to_menu(),
    )
    await callback.answer()
