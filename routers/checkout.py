import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from services.cart_service import get_cart, get_cart_raw, clear_cart
from services.order_service import create_order, add_order_items
from services.product_service import decrease_stock
from services.payment_service import create_payment
from services.delivery_service import deliver_by_product_ids
from ui.keyboards import back_to_menu

logger = logging.getLogger(__name__)

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

    # Step 1: Create order
    try:
        order_id = create_order(user_id, total, "mixed")
    except Exception as e:
        logger.error("Checkout failed at order creation for user %d: %s", user_id, e)
        await callback.message.answer("❌ Checkout failed. Please try again.")
        await callback.answer()
        return

    # Step 2: Add order items
    raw = get_cart_raw(user_id)
    if not raw:
        logger.error("Cart raw data empty during checkout for user %d", user_id)
        await callback.message.answer("❌ Checkout failed — cart data unavailable.")
        await callback.answer()
        return

    try:
        add_order_items(order_id, raw)
    except Exception as e:
        logger.error(
            "Checkout failed at adding order items for order %d: %s", order_id, e
        )
        await callback.message.answer("❌ Checkout failed while processing items.")
        await callback.answer()
        return

    # Step 3: Decrease stock
    product_ids = []
    try:
        for pid, qty in raw:
            decrease_stock(pid, qty)
            product_ids.append(pid)
    except Exception as e:
        logger.error(
            "Checkout failed at stock decrease for order %d: %s", order_id, e
        )
        await callback.message.answer(
            "❌ Some items are out of stock. Order could not be completed."
        )
        await callback.answer()
        return

    # Step 4: Create payment record
    try:
        create_payment(order_id, total)
    except Exception as e:
        logger.error(
            "Checkout: payment creation failed for order %d: %s", order_id, e
        )
        await callback.message.answer(
            f"⚠️ Order #{order_id} created but payment recording failed. "
            "Please contact support."
        )
        await callback.answer()
        return

    # Step 5: Clear cart
    try:
        clear_cart(user_id)
    except Exception as e:
        logger.error("Failed to clear cart after checkout for user %d: %s", user_id, e)
        # Non-fatal: order is already placed

    # Step 6: Deliver digital content
    try:
        await deliver_by_product_ids(callback.bot, user_id, product_ids)
    except Exception as e:
        logger.error(
            "Failed to deliver digital content for order %d: %s", order_id, e
        )
        # Non-fatal: order is placed, just log it

    await callback.message.answer(
        f"<b>Order #{order_id} confirmed</b>\n"
        f"Total: {total}$\n\n"
        "Your digital items have been delivered above.",
        parse_mode="HTML",
        reply_markup=back_to_menu(),
    )
    await callback.answer()
