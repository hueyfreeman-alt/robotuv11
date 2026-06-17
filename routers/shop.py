import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from services.product_service import get_categories, get_products_by_category
from services.cart_service import add_to_cart
from ui.keyboards import category_keyboard, product_actions, back_to_menu

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(lambda c: c.data == "shop")
async def shop(callback: CallbackQuery):
    categories = get_categories()

    if not categories:
        await callback.message.edit_text(
            "No products available.",
            reply_markup=back_to_menu(),
        )
        await callback.answer()
        return

    if len(categories) == 1:
        # Skip category selection if only one
        products = get_products_by_category(categories[0])
        await _show_products(callback, products)
    else:
        await callback.message.edit_text(
            "Select a category:",
            reply_markup=category_keyboard(categories),
        )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("cat_"))
async def category(callback: CallbackQuery):
    cat = callback.data[4:]
    products = get_products_by_category(cat)
    await _show_products(callback, products)
    await callback.answer()


async def _show_products(callback: CallbackQuery, products):
    if not products:
        await callback.message.edit_text(
            "No products in this category.",
            reply_markup=back_to_menu(),
        )
        return

    for p in products:
        pid, name, price, stock, category, ptype = p
        text = (
            f"<b>{name}</b>\n"
            f"Price: {price}$\n"
            f"In stock: {stock}"
        )
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=product_actions(pid),
        )


@router.callback_query(lambda c: c.data and c.data.startswith("add_"))
async def add(callback: CallbackQuery):
    try:
        product_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError) as e:
        logger.warning("Invalid add callback data: %r — %s", callback.data, e)
        await callback.answer("❌ Invalid product")
        return

    try:
        add_to_cart(callback.from_user.id, product_id, 1)
        await callback.answer("Added to cart ✅")
    except Exception as e:
        logger.error("Failed to add product %d to cart: %s", product_id, e)
        await callback.answer("❌ Failed to add item")
