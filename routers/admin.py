import logging

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from ui.keyboards import (
    admin_menu,
    vendor_product_actions,
    delivery_type_keyboard,
    broadcast_type_keyboard,
)
from services.product_service import (
    get_all_products,
    get_product,
    add_product,
    update_product,
    delete_product,
)
from services.delivery_service import (
    get_delivery_items,
    add_delivery_item,
    clear_delivery_items,
)
from services.settings_service import get_setting, set_setting
from services.user_service import get_all_users, get_user_count
from services.broadcast_service import save_broadcast
from services.order_service import update_order_status

logger = logging.getLogger(__name__)

router = Router()


# --- FSM States ---

class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    stock = State()
    category = State()


class EditProduct(StatesGroup):
    field = State()
    value = State()


class DeliveryAdd(StatesGroup):
    content = State()


class PromoMedia(StatesGroup):
    waiting_media = State()


class BroadcastState(StatesGroup):
    waiting_media = State()


# --- Admin access check ---

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# --- Admin Panel Entry ---

@router.message(lambda m: m.text and m.text == "/admin")
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Admin Panel", reply_markup=admin_menu())


@router.callback_query(lambda c: c.data == "admin_panel")
async def admin_panel_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    await state.clear()
    await callback.message.edit_text("Admin Panel", reply_markup=admin_menu())
    await callback.answer()


# --- Stats ---

@router.callback_query(lambda c: c.data == "adm_stats")
async def stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    try:
        user_count = get_user_count()
        products = get_all_products()
    except Exception as e:
        logger.error("Failed to fetch stats: %s", e)
        await callback.answer("Failed to load stats")
        return
    await callback.message.edit_text(
        f"<b>Stats</b>\n\n"
        f"Users: {user_count}\n"
        f"Products: {len(products)}",
        parse_mode="HTML",
        reply_markup=admin_menu(),
    )
    await callback.answer()


# --- Product Management ---

@router.callback_query(lambda c: c.data == "adm_products")
async def list_products(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    products = get_all_products()
    if not products:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add Product", callback_data="adm_addprod")],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")],
        ])
        await callback.message.edit_text("No products yet.", reply_markup=kb)
        await callback.answer()
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    buttons = []
    for p in products:
        pid, name, price, stock, category, ptype = p
        buttons.append([InlineKeyboardButton(
            text=f"{name} — {price}$ (stock: {stock})",
            callback_data=f"vprod_{pid}",
        )])
    buttons.append([InlineKeyboardButton(text="➕ Add Product", callback_data="adm_addprod")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")])

    await callback.message.edit_text(
        "<b>Products</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vprod_"))
async def view_product(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    try:
        product_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError) as e:
        logger.warning("Invalid vprod callback data: %r — %s", callback.data, e)
        await callback.answer("Invalid product")
        return

    p = get_product(product_id)
    if not p:
        await callback.answer("Product not found")
        return

    pid, name, description, price, stock, category, ptype = p
    delivery_items = get_delivery_items(pid)

    delivery_text = ""
    if delivery_items:
        delivery_text = "\n\n<b>Delivery items:</b>\n"
        for dtype, content, file_id in delivery_items:
            label = content[:30] if content else (file_id[:20] if file_id else "—")
            delivery_text += f"  • [{dtype}] {label}\n"

    text = (
        f"<b>{name}</b>\n"
        f"Description: {description or '—'}\n"
        f"Price: {price}$\n"
        f"Stock: {stock}\n"
        f"Category: {category}\n"
        f"Type: {ptype}"
        f"{delivery_text}"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=vendor_product_actions(pid),
    )
    await callback.answer()


# --- Add Product ---

@router.callback_query(lambda c: c.data == "adm_addprod")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    await state.set_state(AddProduct.name)
    await callback.message.edit_text("Enter product name:")
    await callback.answer()


@router.message(AddProduct.name)
async def add_product_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.description)
    await message.answer("Enter description (or send '-' to skip):")


@router.message(AddProduct.description)
async def add_product_desc(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    desc = "" if message.text == "-" else message.text
    await state.update_data(description=desc)
    await state.set_state(AddProduct.price)
    await message.answer("Enter price:")


@router.message(AddProduct.price)
async def add_product_price(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Invalid price. Enter a number:")
        return
    await state.update_data(price=price)
    await state.set_state(AddProduct.stock)
    await message.answer("Enter stock quantity:")


@router.message(AddProduct.stock)
async def add_product_stock(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        stock = int(message.text)
    except ValueError:
        await message.answer("Invalid number. Enter stock quantity:")
        return
    await state.update_data(stock=stock)
    await state.set_state(AddProduct.category)
    await message.answer("Enter category:")


@router.message(AddProduct.category)
async def add_product_category(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    try:
        product_id = add_product(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            stock=data["stock"],
            category=message.text,
            ptype="digital",
        )
    except Exception as e:
        logger.error("Failed to add product: %s", e)
        await state.clear()
        await message.answer("❌ Failed to create product. Check logs.")
        return
    await state.clear()
    await message.answer(
        f"Product #{product_id} created.\n\nAdd delivery items now:",
        reply_markup=delivery_type_keyboard(product_id),
    )


# --- Edit Product ---

@router.callback_query(lambda c: c.data.startswith("vedit_"))
async def edit_product_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    try:
        product_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError) as e:
        logger.warning("Invalid vedit callback data: %r — %s", callback.data, e)
        await callback.answer("Invalid product")
        return

    await state.update_data(edit_product_id=product_id)
    await state.set_state(EditProduct.field)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Name", callback_data="efield_name")],
        [InlineKeyboardButton(text="Description", callback_data="efield_description")],
        [InlineKeyboardButton(text="Price", callback_data="efield_price")],
        [InlineKeyboardButton(text="Stock", callback_data="efield_stock")],
        [InlineKeyboardButton(text="Category", callback_data="efield_category")],
        [InlineKeyboardButton(text="⬅️ Cancel", callback_data=f"vprod_{product_id}")],
    ])
    await callback.message.edit_text("Select field to edit:", reply_markup=kb)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("efield_"))
async def edit_field_selected(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    field = callback.data.split("_", 1)[1]
    await state.update_data(edit_field=field)
    await state.set_state(EditProduct.value)
    await callback.message.edit_text(f"Enter new value for {field}:")
    await callback.answer()


@router.message(EditProduct.value)
async def edit_product_value(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    product_id = data["edit_product_id"]
    field = data["edit_field"]
    value = message.text

    if field == "price":
        try:
            value = float(value)
        except ValueError:
            await message.answer("Invalid price.")
            return
    elif field == "stock":
        try:
            value = int(value)
        except ValueError:
            await message.answer("Invalid number.")
            return

    try:
        update_product(product_id, **{field: value})
    except Exception as e:
        logger.error("Failed to update product %d field %s: %s", product_id, field, e)
        await state.clear()
        await message.answer("❌ Failed to update product.")
        return
    await state.clear()
    await message.answer(f"Updated {field}.", reply_markup=vendor_product_actions(product_id))


# --- Delete Product ---

@router.callback_query(lambda c: c.data.startswith("vdel_"))
async def delete_prod(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    try:
        product_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError) as e:
        logger.warning("Invalid vdel callback data: %r — %s", callback.data, e)
        await callback.answer("Invalid product")
        return
    try:
        delete_product(product_id)
    except Exception as e:
        logger.error("Failed to delete product %d: %s", product_id, e)
        await callback.answer("❌ Failed to delete product")
        return
    await callback.message.edit_text("Product deleted.", reply_markup=admin_menu())
    await callback.answer()


# --- Delivery Management ---

@router.callback_query(lambda c: c.data == "adm_delivery")
async def delivery_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    products = get_all_products()
    if not products:
        await callback.message.edit_text("No products. Add products first.", reply_markup=admin_menu())
        await callback.answer()
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    buttons = []
    for p in products:
        pid, name, price, stock, category, ptype = p
        items = get_delivery_items(pid)
        count = len(items)
        buttons.append([InlineKeyboardButton(
            text=f"{name} ({count} items)",
            callback_data=f"vdeliv_{pid}",
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")])

    await callback.message.edit_text(
        "<b>Delivery Management</b>\nSelect a product:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vdeliv_"))
async def view_delivery(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    try:
        product_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError) as e:
        logger.warning("Invalid vdeliv callback data: %r — %s", callback.data, e)
        await callback.answer("Invalid product")
        return

    items = get_delivery_items(product_id)
    p = get_product(product_id)
    name = p[1] if p else "Unknown"

    if not items:
        text = f"<b>{name}</b>\n\nNo delivery items configured."
    else:
        text = f"<b>{name}</b>\n\n<b>Delivery items:</b>\n"
        for dtype, content, file_id in items:
            label = content[:40] if content else (file_id[:20] if file_id else "—")
            text += f"  • [{dtype}] {label}\n"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add Item", callback_data=f"dadd_menu_{product_id}")],
        [InlineKeyboardButton(text="🗑 Clear All", callback_data=f"dclear_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"vprod_{product_id}")],
    ])

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("dadd_menu_"))
async def delivery_add_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    try:
        product_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError) as e:
        logger.warning("Invalid dadd_menu callback data: %r — %s", callback.data, e)
        await callback.answer("Invalid product")
        return
    await callback.message.edit_text(
        "Select delivery type:",
        reply_markup=delivery_type_keyboard(product_id),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("dadd_"))
async def delivery_add_type(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    parts = callback.data.split("_")
    # dadd_text_1, dadd_photo_1, etc.
    if len(parts) < 3:
        await callback.answer()
        return

    dtype = parts[1]
    try:
        product_id = int(parts[2])
    except (ValueError, IndexError) as e:
        logger.warning("Invalid dadd callback data: %r — %s", callback.data, e)
        await callback.answer("Invalid product")
        return

    if dtype == "menu":
        return

    await state.update_data(delivery_product_id=product_id, delivery_type=dtype)
    await state.set_state(DeliveryAdd.content)

    prompts = {
        "text": "Send the text content:",
        "photo": "Send a photo:",
        "video": "Send a video:",
        "file": "Send a file:",
        "coords": "Send coordinates (lat,lon):",
    }
    await callback.message.edit_text(prompts.get(dtype, "Send content:"))
    await callback.answer()


@router.message(DeliveryAdd.content)
async def delivery_add_content(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    product_id = data["delivery_product_id"]
    dtype = data["delivery_type"]

    content = ""
    file_id = None

    if dtype == "text":
        content = message.text or ""
    elif dtype == "coords":
        content = message.text or ""
    elif dtype == "photo":
        if message.photo:
            file_id = message.photo[-1].file_id
            content = message.caption or ""
        else:
            await message.answer("Please send a photo.")
            return
    elif dtype == "video":
        if message.video:
            file_id = message.video.file_id
            content = message.caption or ""
        else:
            await message.answer("Please send a video.")
            return
    elif dtype == "file":
        if message.document:
            file_id = message.document.file_id
            content = message.caption or ""
        else:
            await message.answer("Please send a file.")
            return

    # Map 'coords' back to 'coordinates' for storage
    store_type = "coordinates" if dtype == "coords" else dtype
    try:
        add_delivery_item(product_id, store_type, content, file_id)
    except Exception as e:
        logger.error("Failed to add delivery item for product %d: %s", product_id, e)
        await state.clear()
        await message.answer("❌ Failed to add delivery item.")
        return
    await state.clear()
    await message.answer(
        f"Delivery item ({store_type}) added.",
        reply_markup=delivery_type_keyboard(product_id),
    )


@router.callback_query(lambda c: c.data.startswith("dclear_"))
async def delivery_clear(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    try:
        product_id = int(callback.data.split("_")[1])
    except (ValueError, IndexError) as e:
        logger.warning("Invalid dclear callback data: %r — %s", callback.data, e)
        await callback.answer("Invalid product")
        return
    try:
        clear_delivery_items(product_id)
    except Exception as e:
        logger.error("Failed to clear delivery items for product %d: %s", product_id, e)
        await callback.answer("❌ Failed to clear delivery items")
        return
    await callback.message.edit_text(
        "All delivery items cleared.",
        reply_markup=delivery_type_keyboard(product_id),
    )
    await callback.answer()


# --- Promo Media ---

@router.callback_query(lambda c: c.data == "adm_promo")
async def promo_menu(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    current_type = get_setting("promo_type", "none")
    current_caption = get_setting("promo_caption", "")

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📷 Set Photo", callback_data="promo_set_photo")],
        [InlineKeyboardButton(text="🎬 Set Video", callback_data="promo_set_video")],
        [InlineKeyboardButton(text="🎞 Set GIF", callback_data="promo_set_gif")],
        [InlineKeyboardButton(text="🗑 Remove Promo", callback_data="promo_remove")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")],
    ])

    await callback.message.edit_text(
        f"<b>Promo Media</b>\n\n"
        f"Current: {current_type}\n"
        f"Caption: {current_caption or '—'}",
        parse_mode="HTML",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("promo_set_"))
async def promo_set(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    media_type = callback.data.split("_")[2]  # photo, video, gif
    await state.update_data(promo_media_type=media_type)
    await state.set_state(PromoMedia.waiting_media)
    await callback.message.edit_text(f"Send a {media_type} for the /start promo:")
    await callback.answer()


@router.message(PromoMedia.waiting_media)
async def promo_receive(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    media_type = data["promo_media_type"]
    file_id = None
    caption = ""

    if media_type == "photo" and message.photo:
        file_id = message.photo[-1].file_id
        caption = message.caption or ""
    elif media_type == "video" and message.video:
        file_id = message.video.file_id
        caption = message.caption or ""
    elif media_type == "gif" and message.animation:
        file_id = message.animation.file_id
        caption = message.caption or ""
    else:
        await message.answer(f"Please send a valid {media_type}.")
        return

    try:
        set_setting("promo_type", media_type)
        set_setting("promo_file_id", file_id)
        set_setting("promo_caption", caption)
    except Exception as e:
        logger.error("Failed to save promo settings: %s", e)
        await state.clear()
        await message.answer("❌ Failed to save promo media.")
        return
    await state.clear()
    await message.answer("Promo media updated.", reply_markup=admin_menu())


@router.callback_query(lambda c: c.data == "promo_remove")
async def promo_remove(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    try:
        set_setting("promo_type", "")
        set_setting("promo_file_id", "")
        set_setting("promo_caption", "")
    except Exception as e:
        logger.error("Failed to remove promo settings: %s", e)
        await callback.answer("❌ Failed to remove promo media")
        return
    await callback.message.edit_text("Promo media removed.", reply_markup=admin_menu())
    await callback.answer()


# --- Broadcast ---

@router.callback_query(lambda c: c.data == "adm_broadcast")
async def broadcast_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    try:
        user_count = get_user_count()
    except Exception as e:
        logger.error("Failed to get user count for broadcast: %s", e)
        await callback.answer("❌ Failed to load broadcast info")
        return
    await callback.message.edit_text(
        f"<b>Broadcast</b>\n\nRecipients: {user_count} users\n\nSelect media type:",
        parse_mode="HTML",
        reply_markup=broadcast_type_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("bc_"))
async def broadcast_type(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return

    media_type = callback.data.split("_")[1]  # photo or video
    await state.update_data(bc_type=media_type)
    await state.set_state(BroadcastState.waiting_media)
    await callback.message.edit_text(f"Send a {media_type} to broadcast:")
    await callback.answer()


@router.message(BroadcastState.waiting_media)
async def broadcast_send(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    media_type = data["bc_type"]
    file_id = None
    caption = ""

    if media_type == "photo" and message.photo:
        file_id = message.photo[-1].file_id
        caption = message.caption or ""
    elif media_type == "video" and message.video:
        file_id = message.video.file_id
        caption = message.caption or ""
    else:
        await message.answer(f"Please send a valid {media_type}.")
        return

    await state.clear()

    users = get_all_users()
    sent = 0
    failed = 0

    for uid in users:
        try:
            if media_type == "photo":
                await message.bot.send_photo(uid, file_id, caption=caption or None)
            elif media_type == "video":
                await message.bot.send_video(uid, file_id, caption=caption or None)
            sent += 1
        except Exception as e:
            logger.warning("Broadcast failed for user %d: %s", uid, e)
            failed += 1

    try:
        save_broadcast(media_type, file_id, caption)
    except Exception as e:
        logger.error("Failed to save broadcast record: %s", e)

    await message.answer(
        f"<b>Broadcast complete</b>\n\n"
        f"Sent: {sent}\n"
        f"Failed: {failed}",
        parse_mode="HTML",
        reply_markup=admin_menu(),
    )


# --- Order Status (legacy command support) ---

@router.message(lambda m: m.text and m.text.startswith("/set"))
async def set_status(message: Message):
    if not is_admin(message.from_user.id):
        return

    try:
        _, order_id_str, status = message.text.split("|")
        order_id = int(order_id_str.strip())
        status = status.strip()
    except (ValueError, TypeError) as e:
        logger.warning("Admin sent malformed /set command: %r — %s", message.text, e)
        await message.answer("❌ Format: /set|id|status")
        return

    try:
        update_order_status(order_id, status)
        await message.answer(f"✅ Order {order_id} → {status}")
    except ValueError as e:
        await message.answer(f"❌ {e}")
    except Exception as e:
        logger.error("Failed to update order %d: %s", order_id, e)
        await message.answer("❌ Failed to update order. Check logs.")
