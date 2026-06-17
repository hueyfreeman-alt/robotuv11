from aiogram import Router
from aiogram.types import CallbackQuery

from services.cart_service import get_cart, clear_cart
from services.user_service import get_balance, deduct_balance
from services.order_service import create_order, add_order_items
from services.product_service import decrease_stock, get_product
from services.vendor_service import credit_vendor_wallet
from services.delivery_service import deliver_digital
from ui.keyboards import back_to_menu

router = Router()


@router.callback_query(lambda c: c.data == "checkout")
async def checkout(callback: CallbackQuery):
    items = get_cart(callback.from_user.id)
    if not items:
        await callback.message.edit_text("Cart is empty.", reply_markup=back_to_menu())
        await callback.answer()
        return

    total = sum(price * qty for _, _, price, qty, _ in items)
    balance = get_balance(callback.from_user.id)

    if balance < total:
        await callback.message.edit_text(
            f"Insufficient balance.\n\nRequired: {total:.2f}$\nYour balance: {balance:.2f}$\n\nPlease deposit funds first.",
            reply_markup=back_to_menu(),
        )
        await callback.answer()
        return

    # Group items by vendor
    vendor_items = {}
    for product_id, name, price, qty, vendor_id in items:
        if vendor_id not in vendor_items:
            vendor_items[vendor_id] = []
        vendor_items[vendor_id].append((product_id, qty, price))

    # Process each vendor's order
    deduct_balance(callback.from_user.id, total)
    product_ids = []

    for vendor_id, v_items in vendor_items.items():
        vendor_total = sum(p * q for _, q, p in v_items)
        order_id = create_order(callback.from_user.id, vendor_id, vendor_total)
        add_order_items(order_id, [(pid, qty) for pid, qty, _ in v_items])

        # Credit vendor wallet
        credit_vendor_wallet(vendor_id, vendor_total)

        # Decrease stock
        for pid, qty, _ in v_items:
            product = get_product(pid)
            if product and product[6] > 0:
                decrease_stock(pid, qty)
            product_ids.append(pid)

    # Deliver digital content
    await deliver_digital(callback.message.bot, callback.from_user.id, product_ids)

    clear_cart(callback.from_user.id)

    await callback.message.edit_text(
        f"<b>Purchase complete!</b>\n\nTotal: {total:.2f}$\nRemaining balance: {balance - total:.2f}$\n\nDigital items delivered above.",
        parse_mode="HTML",
        reply_markup=back_to_menu(),
    )
    await callback.answer()
