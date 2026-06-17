from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from services.vendor_service import (
    create_city, get_all_cities, delete_city, get_all_vendors, get_pending_withdrawals, update_withdrawal_status,
)
from services.settings_service import get_setting, set_setting
from services.user_service import get_all_users, get_user_count
from services.broadcast_service import save_broadcast
from ui.keyboards import admin_menu, broadcast_type_keyboard, back_to_menu

router = Router()


class AdminCity(StatesGroup):
    name = State()


class PromoMedia(StatesGroup):
    media = State()


class BroadcastState(StatesGroup):
    media = State()
    caption = State()


def is_admin(telegram_id):
    return telegram_id == ADMIN_ID


@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("<b>Admin Panel</b>", parse_mode="HTML", reply_markup=admin_menu())


@router.callback_query(lambda c: c.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    await callback.message.edit_text("<b>Admin Panel</b>", parse_mode="HTML", reply_markup=admin_menu())
    await callback.answer()


# --- Cities ---

@router.callback_query(lambda c: c.data == "adm_cities")
async def adm_cities(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    cities = get_all_cities()
    buttons = []
    for city_id, name, _ in cities:
        buttons.append([
            InlineKeyboardButton(text=f"🏙 {name}", callback_data=f"adm_city_{city_id}"),
            InlineKeyboardButton(text="❌", callback_data=f"adm_delcity_{city_id}"),
        ])
    buttons.append([InlineKeyboardButton(text="➕ Add City", callback_data="adm_addcity")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")])

    await callback.message.edit_text(
        "<b>Cities</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "adm_addcity")
async def adm_add_city(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AdminCity.name)
    await callback.message.edit_text("Enter city name:")
    await callback.answer()


@router.message(AdminCity.name)
async def adm_city_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        create_city(message.text)
        await message.answer(f"City '{message.text}' created.", reply_markup=back_to_menu())
    except Exception:
        await message.answer("City already exists or invalid name.", reply_markup=back_to_menu())
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("adm_delcity_"))
async def adm_del_city(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    city_id = int(callback.data.split("_")[2])
    delete_city(city_id)
    await callback.answer("City removed")
    # Refresh
    cities = get_all_cities()
    buttons = []
    for cid, name, _ in cities:
        buttons.append([
            InlineKeyboardButton(text=f"🏙 {name}", callback_data=f"adm_city_{cid}"),
            InlineKeyboardButton(text="❌", callback_data=f"adm_delcity_{cid}"),
        ])
    buttons.append([InlineKeyboardButton(text="➕ Add City", callback_data="adm_addcity")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")])
    await callback.message.edit_text(
        "<b>Cities</b>", parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


# --- Vendors ---

@router.callback_query(lambda c: c.data == "adm_vendors")
async def adm_vendors(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    vendors = get_all_vendors()
    if not vendors:
        await callback.message.edit_text("No vendors.", reply_markup=admin_menu())
        await callback.answer()
        return

    buttons = []
    for v in vendors:
        vid, tid, city_id, shop_name, _, is_active, wallet = v
        status = "✅" if is_active else "❌"
        buttons.append([InlineKeyboardButton(
            text=f"{status} {shop_name} (wallet: {wallet:.2f}$)",
            callback_data=f"adm_vendor_{vid}",
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")])

    await callback.message.edit_text(
        "<b>Vendors</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


# --- Withdrawals ---

@router.callback_query(lambda c: c.data == "adm_withdrawals")
async def adm_withdrawals(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    pending = get_pending_withdrawals()
    if not pending:
        await callback.message.edit_text("No pending withdrawals.", reply_markup=admin_menu())
        await callback.answer()
        return

    buttons = []
    for w_id, vendor_id, amount, created, shop_name in pending:
        buttons.append([
            InlineKeyboardButton(text=f"{shop_name}: {amount}$", callback_data=f"adm_w_{w_id}"),
            InlineKeyboardButton(text="✅", callback_data=f"adm_wappr_{w_id}"),
            InlineKeyboardButton(text="❌", callback_data=f"adm_wrej_{w_id}"),
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")])

    await callback.message.edit_text(
        "<b>Pending Withdrawals</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("adm_wappr_"))
async def adm_approve_withdrawal(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    w_id = int(callback.data.split("_")[2])
    update_withdrawal_status(w_id, "approved")
    await callback.answer("Approved")
    await callback.message.edit_text("Withdrawal approved.", reply_markup=admin_menu())


@router.callback_query(lambda c: c.data.startswith("adm_wrej_"))
async def adm_reject_withdrawal(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    w_id = int(callback.data.split("_")[2])
    update_withdrawal_status(w_id, "rejected")
    await callback.answer("Rejected")
    await callback.message.edit_text("Withdrawal rejected.", reply_markup=admin_menu())


# --- Promo Media ---

@router.callback_query(lambda c: c.data == "adm_promo")
async def adm_promo(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    current_type = get_setting("promo_type") or "None"
    await state.set_state(PromoMedia.media)
    await callback.message.edit_text(
        f"Current promo: {current_type}\n\nSend a GIF, video, or photo to set as promo:"
    )
    await callback.answer()


@router.message(PromoMedia.media)
async def adm_promo_media(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    if message.animation:
        set_setting("promo_type", "gif")
        set_setting("promo_file_id", message.animation.file_id)
    elif message.video:
        set_setting("promo_type", "video")
        set_setting("promo_file_id", message.video.file_id)
    elif message.photo:
        set_setting("promo_type", "photo")
        set_setting("promo_file_id", message.photo[-1].file_id)
    else:
        await message.answer("Send a GIF, video, or photo.")
        return

    set_setting("promo_caption", message.caption or "")
    await state.clear()
    await message.answer("Promo media updated.", reply_markup=back_to_menu())


# --- Broadcast ---

@router.callback_query(lambda c: c.data == "adm_broadcast")
async def adm_broadcast(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    await callback.message.edit_text(
        "Select broadcast type:",
        reply_markup=broadcast_type_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("bc_"))
async def adm_bc_type(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    bc_type = callback.data.split("_")[1]
    await state.update_data(bc_type=bc_type)
    await state.set_state(BroadcastState.media)
    await callback.message.edit_text(f"Send the {bc_type} for broadcast:")
    await callback.answer()


@router.message(BroadcastState.media)
async def adm_bc_media(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    bc_type = data["bc_type"]

    file_id = None
    if bc_type == "photo" and message.photo:
        file_id = message.photo[-1].file_id
    elif bc_type == "video" and message.video:
        file_id = message.video.file_id
    else:
        await message.answer(f"Send a valid {bc_type}.")
        return

    caption = message.caption or ""
    save_broadcast(bc_type, file_id, caption)

    # Send to all users
    users = get_all_users()
    sent = 0
    for user_id in users:
        try:
            if bc_type == "photo":
                await message.bot.send_photo(user_id, file_id, caption=caption or None)
            else:
                await message.bot.send_video(user_id, file_id, caption=caption or None)
            sent += 1
        except Exception:
            pass

    await state.clear()
    await message.answer(
        f"Broadcast sent to {sent}/{len(users)} users.",
        reply_markup=back_to_menu(),
    )


# --- Stats ---

@router.callback_query(lambda c: c.data == "adm_stats")
async def adm_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    user_count = get_user_count()
    vendors = get_all_vendors()
    cities = get_all_cities()

    text = (
        f"<b>Stats</b>\n\n"
        f"Users: {user_count}\n"
        f"Vendors: {len(vendors)}\n"
        f"Cities: {len(cities)}"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")],
        ]),
    )
    await callback.answer()
