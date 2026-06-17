from aiogram import Router
from aiogram.types import CallbackQuery

from services.vendor_service import get_all_cities, get_vendors_by_city, get_vendor
from services.product_service import get_available_products_by_vendor, get_product
from services.cart_service import add_to_cart
from services.review_service import get_product_rating, get_vendor_rating
from ui.keyboards import city_keyboard, vendor_keyboard, product_card_keyboard, back_to_menu

router = Router()


@router.callback_query(lambda c: c.data == "shop")
async def shop(callback: CallbackQuery):
    cities = get_all_cities()
    if not cities:
        await callback.message.edit_text("No cities available yet.", reply_markup=back_to_menu())
        await callback.answer()
        return

    await callback.message.edit_text(
        "<b>Select a city:</b>",
        parse_mode="HTML",
        reply_markup=city_keyboard(cities),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("city_"))
async def city_vendors(callback: CallbackQuery):
    city_id = int(callback.data.split("_")[1])
    vendors = get_vendors_by_city(city_id)

    if not vendors:
        await callback.message.edit_text("No shops in this city yet.", reply_markup=back_to_menu())
        await callback.answer()
        return

    await callback.message.edit_text(
        "<b>Select a shop:</b>",
        parse_mode="HTML",
        reply_markup=vendor_keyboard(vendors),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vendor_"))
async def vendor_products(callback: CallbackQuery):
    vendor_id = int(callback.data.split("_")[1])
    vendor = get_vendor(vendor_id)
    if not vendor:
        await callback.answer("Shop not found")
        return

    _, _, _, shop_name, shop_desc, _, _ = vendor
    avg_rating, review_count = get_vendor_rating(vendor_id)

    products = get_available_products_by_vendor(vendor_id)

    header = (
        f"<b>🏪 {shop_name}</b>\n"
        f"{shop_desc}\n"
        f"Rating: {'⭐' * int(avg_rating)} {avg_rating}/5 ({review_count} reviews)\n"
    )

    if not products:
        await callback.message.edit_text(
            header + "\nNo products available.",
            parse_mode="HTML",
            reply_markup=back_to_menu(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(header, parse_mode="HTML")

    for p in products:
        pid, _, _, name, desc, price, stock, cat, ptype, preorder = p
        avg_r, r_count = get_product_rating(pid)
        stock_text = f"In stock: {stock}" if stock > 0 else "Preorder available"

        text = (
            f"<b>{name}</b>\n"
            f"{desc}\n"
            f"Price: {price}$\n"
            f"{stock_text}\n"
            f"Rating: {'⭐' * int(avg_r)} {avg_r}/5 ({r_count})"
        )
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=product_card_keyboard(pid, stock > 0, preorder),
        )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("add_"))
async def add_to_cart_handler(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = get_product(product_id)
    if not product:
        await callback.answer("Product not found")
        return
    if product[6] <= 0:
        await callback.answer("Out of stock")
        return

    add_to_cart(callback.from_user.id, product_id, 1)
    await callback.answer("Added to cart")


@router.callback_query(lambda c: c.data.startswith("preorder_"))
async def preorder_handler(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = get_product(product_id)
    if not product:
        await callback.answer("Product not found")
        return

    add_to_cart(callback.from_user.id, product_id, 1)
    await callback.answer("Preorder added to cart")
