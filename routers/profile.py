from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import SHOP_SLOT_PRICE
from services.user_service import get_user, get_balance, deduct_balance, set_role
from services.order_service import get_user_orders, get_order
from services.vendor_service import get_vendor, get_vendor_by_telegram, get_all_cities, create_vendor
from ui.keyboards import profile_keyboard, back_to_menu, order_actions

router = Router()


class UpgradeState(StatesGroup):
    city = State()
    shop_name = State()


@router.callback_query(lambda c: c.data == "profile")
async def profile(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.message.edit_text("Profile not found.", reply_markup=back_to_menu())
        await callback.answer()
        return

    _, username, balance, role, joined = user
    is_vendor = get_vendor_by_telegram(callback.from_user.id) is not None

    text = (
        f"<b>Profile</b>\n\n"
        f"Username: @{username or '—'}\n"
        f"Balance: {balance:.2f}$\n"
        f"Role: {role}\n"
        f"Joined: {joined[:10] if joined else '—'}"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=profile_keyboard(is_vendor)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "upgrade_vendor")
async def upgrade_vendor(callback: CallbackQuery, state: FSMContext):
    # Check if already a vendor
    if get_vendor_by_telegram(callback.from_user.id):
        await callback.answer("You are already a vendor")
        return

    balance = get_balance(callback.from_user.id)
    from services.settings_service import get_setting
    slot_price = float(get_setting("shop_slot_price") or SHOP_SLOT_PRICE)

    # Show upgrade info with rules
    rules = get_setting("vendor_rules") or (
        "1. Deliver all orders on time.\n"
        "2. Respond to tickets within 24h.\n"
        "3. No scamming or fake products.\n"
        "4. Violations result in shop closure."
    )

    text = (
        f"<b>⬆️ Become a Vendor</b>\n\n"
        f"Price: {slot_price}$\n"
        f"Your balance: {balance:.2f}$\n\n"
        f"<b>Vendor Rules:</b>\n{rules}\n\n"
        f"By upgrading, you agree to these rules."
    )

    if balance < slot_price:
        text += f"\n\n<i>Insufficient balance. Deposit {slot_price - balance:.2f}$ more.</i>"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_to_menu())
        await callback.answer()
        return

    # Show cities to pick from
    cities = get_all_cities()
    if not cities:
        await callback.message.edit_text(
            text + "\n\n<i>No cities available. Contact admin.</i>",
            parse_mode="HTML",
            reply_markup=back_to_menu(),
        )
        await callback.answer()
        return

    buttons = []
    for city_id, name, _ in cities:
        buttons.append([InlineKeyboardButton(text=f"🏙 {name}", callback_data=f"upgcity_{city_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Cancel", callback_data="profile")])

    await callback.message.edit_text(
        text + "\n\nSelect your city:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("upgcity_"))
async def upgrade_select_city(callback: CallbackQuery, state: FSMContext):
    city_id = int(callback.data.split("_")[1])
    await state.update_data(upgrade_city_id=city_id)
    await state.set_state(UpgradeState.shop_name)
    await callback.message.edit_text("Enter your shop name:")
    await callback.answer()


@router.message(UpgradeState.shop_name)
async def upgrade_shop_name(message: Message, state: FSMContext):
    data = await state.get_data()
    city_id = data["upgrade_city_id"]
    shop_name = message.text

    from services.settings_service import get_setting
    slot_price = float(get_setting("shop_slot_price") or SHOP_SLOT_PRICE)

    balance = get_balance(message.from_user.id)
    if balance < slot_price:
        await state.clear()
        await message.answer("Insufficient balance.", reply_markup=back_to_menu())
        return

    # Deduct and create vendor
    deduct_balance(message.from_user.id, slot_price)
    create_vendor(message.from_user.id, city_id, shop_name)
    set_role(message.from_user.id, "vendor")

    await state.clear()
    await message.answer(
        f"<b>Congratulations!</b>\n\n"
        f"Your shop <b>{shop_name}</b> is now active.\n"
        f"Use /vendor to access your vendor panel.",
        parse_mode="HTML",
        reply_markup=back_to_menu(),
    )


@router.callback_query(lambda c: c.data == "my_orders")
async def my_orders(callback: CallbackQuery):
    orders = get_user_orders(callback.from_user.id)
    if not orders:
        is_vendor = get_vendor_by_telegram(callback.from_user.id) is not None
        await callback.message.edit_text("No orders yet.", reply_markup=profile_keyboard(is_vendor))
        await callback.answer()
        return

    buttons = []
    for o in orders[:15]:
        oid, _, vendor_id, total, status, dtype, reviewed, created = o
        v = get_vendor(vendor_id)
        shop = v[3] if v else "Unknown"
        label = f"#{oid} | {total}$ | {status} | {shop}"
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"vieworder_{oid}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="profile")])

    await callback.message.edit_text(
        "<b>Your Orders</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vieworder_"))
async def view_order(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[1])
    order = get_order(order_id)
    if not order or order[1] != callback.from_user.id:
        await callback.answer("Order not found")
        return

    oid, _, vendor_id, total, status, dtype, reviewed, created = order
    v = get_vendor(vendor_id)
    shop = v[3] if v else "Unknown"

    text = (
        f"<b>Order #{oid}</b>\n\n"
        f"Shop: {shop}\n"
        f"Total: {total}$\n"
        f"Status: {status}\n"
        f"Type: {dtype}\n"
        f"Date: {created[:16] if created else '—'}"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=order_actions(oid)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "cart")
async def cart_redirect(callback: CallbackQuery):
    from services.cart_service import get_cart
    from ui.keyboards import cart_keyboard

    items = get_cart(callback.from_user.id)
    if not items:
        await callback.message.edit_text("Cart is empty.", reply_markup=back_to_menu())
        await callback.answer()
        return

    total = sum(price * qty for _, _, price, qty, _ in items)
    lines = []
    for _, name, price, qty, _ in items:
        lines.append(f"  {name} x{qty} — {price * qty:.2f}$")

    text = (
        "<b>🛒 Your Cart</b>\n\n"
        + "\n".join(lines)
        + f"\n\n<b>Total: {total:.2f}$</b>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=cart_keyboard())
    await callback.answer()
