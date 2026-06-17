from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.vendor_service import get_all_cities, get_vendors_by_city
from services.product_service import get_available_products_by_vendor, get_product
from services.user_service import get_balance, deduct_balance
from services.order_service import create_order, add_order_items
from services.vendor_service import credit_vendor_wallet
from services.courier_service import create_courier_order
from ui.keyboards import back_to_menu

router = Router()


class CourierState(StatesGroup):
    address = State()


@router.callback_query(lambda c: c.data == "courier")
async def courier_menu(callback: CallbackQuery):
    cities = get_all_cities()
    if not cities:
        await callback.message.edit_text("No cities available.", reply_markup=back_to_menu())
        await callback.answer()
        return

    buttons = []
    for city_id, name, _ in cities:
        buttons.append([InlineKeyboardButton(text=f"🏙 {name}", callback_data=f"crcity_{city_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_menu")])

    await callback.message.edit_text(
        "<b>📦 Courier Delivery</b>\n\nSelect city for physical delivery:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("crcity_"))
async def courier_city(callback: CallbackQuery):
    city_id = int(callback.data.split("_")[1])
    vendors = get_vendors_by_city(city_id)
    if not vendors:
        await callback.message.edit_text("No shops with physical delivery.", reply_markup=back_to_menu())
        await callback.answer()
        return

    buttons = []
    for v in vendors:
        vid, _, _, shop_name, _, _, _ = v
        buttons.append([InlineKeyboardButton(text=f"🏪 {shop_name}", callback_data=f"crvendor_{vid}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="courier")])

    await callback.message.edit_text(
        "<b>Select a shop:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("crvendor_"))
async def courier_vendor_products(callback: CallbackQuery):
    vendor_id = int(callback.data.split("_")[1])
    products = get_available_products_by_vendor(vendor_id)
    physical = [p for p in products if p[7] == "physical"]

    if not physical:
        await callback.message.edit_text("No physical products available.", reply_markup=back_to_menu())
        await callback.answer()
        return

    buttons = []
    for p in physical:
        pid, _, _, name, _, price, stock, _, _, preorder = p
        label = f"{name} — {price}$"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"crprod_{pid}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="courier")])

    await callback.message.edit_text(
        "<b>Physical products:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("crprod_"))
async def courier_product(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    product = get_product(product_id)
    if not product:
        await callback.answer("Product not found")
        return

    pid, vendor_id, _, name, desc, price, stock, _, _, preorder = product

    balance = get_balance(callback.from_user.id)
    if balance < price:
        await callback.message.edit_text(
            f"Insufficient balance. Need {price}$, have {balance:.2f}$.",
            reply_markup=back_to_menu(),
        )
        await callback.answer()
        return

    await state.update_data(cr_product_id=pid, cr_vendor_id=vendor_id, cr_price=price)
    await state.set_state(CourierState.address)
    await callback.message.edit_text(
        f"<b>{name}</b>\n{desc}\nPrice: {price}$\n\nEnter your delivery address (easybox/pickup point):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(CourierState.address)
async def courier_address(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data["cr_product_id"]
    vendor_id = data["cr_vendor_id"]
    price = data["cr_price"]
    address = message.text

    # Deduct balance, create preorder
    deduct_balance(message.from_user.id, price)
    order_id = create_order(message.from_user.id, vendor_id, price, "physical")
    add_order_items(order_id, [(product_id, 1)])
    create_courier_order(order_id, message.from_user.id, vendor_id, address)
    credit_vendor_wallet(vendor_id, price)

    await state.clear()
    await message.answer(
        f"<b>Preorder placed!</b>\n\n"
        f"Order #{order_id}\n"
        f"Delivery address: {address}\n"
        f"The vendor will process your order.",
        parse_mode="HTML",
        reply_markup=back_to_menu(),
    )
