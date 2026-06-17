from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.vendor_service import (
    get_vendor_by_telegram, update_vendor,
    get_vendor_wallet_balance, debit_vendor_wallet, request_withdrawal,
)
from services.product_service import (
    get_products_by_vendor, get_product, add_product, update_product, delete_product,
    get_product_owner,
)
from services.delivery_service import (
    get_delivery_items, add_delivery_item, clear_delivery_items,
)
from services.order_service import get_vendor_orders, get_order, update_order_status
from services.ticket_service import get_vendor_tickets, get_ticket, get_ticket_messages, add_ticket_message, respond_ticket
from services.review_service import get_vendor_rating, get_vendor_reviews
from ui.keyboards import vendor_menu, vendor_product_actions, delivery_type_keyboard, back_to_menu

router = Router()


class VendorAddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    stock = State()
    category = State()
    ptype = State()


class VendorEditProduct(StatesGroup):
    field = State()
    value = State()


class DeliveryAdd(StatesGroup):
    content = State()
    file = State()


class VendorSettings(StatesGroup):
    shop_name = State()
    shop_desc = State()


class VendorTicketReply(StatesGroup):
    message = State()


class VendorWithdraw(StatesGroup):
    amount = State()


def _is_vendor(telegram_id):
    return get_vendor_by_telegram(telegram_id)


@router.message(Command("vendor"))
async def vendor_panel_cmd(message: Message):
    vendor = _is_vendor(message.from_user.id)
    if not vendor:
        await message.answer("You are not a vendor.", reply_markup=back_to_menu())
        return
    await message.answer(
        f"<b>Vendor Panel</b>\n🏪 {vendor[3]}",
        parse_mode="HTML",
        reply_markup=vendor_menu(),
    )


@router.callback_query(lambda c: c.data == "vendor_panel")
async def vendor_panel(callback: CallbackQuery):
    vendor = _is_vendor(callback.from_user.id)
    if not vendor:
        await callback.answer("Not a vendor")
        return
    await callback.message.edit_text(
        f"<b>Vendor Panel</b>\n🏪 {vendor[3]}",
        parse_mode="HTML",
        reply_markup=vendor_menu(),
    )
    await callback.answer()


# --- Products ---

@router.callback_query(lambda c: c.data == "vp_products")
async def vp_products(callback: CallbackQuery):
    vendor = _is_vendor(callback.from_user.id)
    if not vendor:
        await callback.answer("Not a vendor")
        return

    products = get_products_by_vendor(vendor[0])
    buttons = []
    for p in products:
        pid, _, _, name, _, price, stock, _, _, _ = p
        buttons.append([InlineKeyboardButton(
            text=f"{name} — {price}$ (stock:{stock})",
            callback_data=f"vpprod_{pid}",
        )])
    buttons.append([InlineKeyboardButton(text="➕ Add Product", callback_data="vp_addprod")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="vendor_panel")])

    await callback.message.edit_text(
        "<b>Your Products</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vpprod_"))
async def vp_product_detail(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    vendor = _is_vendor(callback.from_user.id)
    if not vendor or get_product_owner(product_id) != vendor[0]:
        await callback.answer("Access denied")
        return

    product = get_product(product_id)
    pid, _, _, name, desc, price, stock, cat, ptype, preorder = product
    items = get_delivery_items(pid)

    text = (
        f"<b>{name}</b>\n"
        f"Description: {desc}\n"
        f"Price: {price}$\n"
        f"Stock: {stock}\n"
        f"Category: {cat}\n"
        f"Type: {ptype}\n"
        f"Preorder: {'Yes' if preorder else 'No'}\n"
        f"Delivery items: {len(items)}"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=vendor_product_actions(pid)
    )
    await callback.answer()


# --- Add Product ---

@router.callback_query(lambda c: c.data == "vp_addprod")
async def vp_add_product(callback: CallbackQuery, state: FSMContext):
    vendor = _is_vendor(callback.from_user.id)
    if not vendor:
        await callback.answer("Not a vendor")
        return
    await state.set_state(VendorAddProduct.name)
    await callback.message.edit_text("Enter product name:")
    await callback.answer()


@router.message(VendorAddProduct.name)
async def vp_add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(VendorAddProduct.description)
    await message.answer("Enter description:")


@router.message(VendorAddProduct.description)
async def vp_add_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(VendorAddProduct.price)
    await message.answer("Enter price (number):")


@router.message(VendorAddProduct.price)
async def vp_add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except (ValueError, TypeError):
        await message.answer("Invalid price. Enter a number:")
        return
    await state.update_data(price=price)
    await state.set_state(VendorAddProduct.stock)
    await message.answer("Enter stock quantity (0 for preorder only):")


@router.message(VendorAddProduct.stock)
async def vp_add_stock(message: Message, state: FSMContext):
    try:
        stock = int(message.text)
    except (ValueError, TypeError):
        await message.answer("Invalid number. Enter stock:")
        return
    await state.update_data(stock=stock)
    await state.set_state(VendorAddProduct.category)
    await message.answer("Enter category (e.g. digital, physical):")


@router.message(VendorAddProduct.category)
async def vp_add_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(VendorAddProduct.ptype)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Digital", callback_data="ptype_digital")],
        [InlineKeyboardButton(text="Physical", callback_data="ptype_physical")],
    ])
    await message.answer("Select product type:", reply_markup=kb)


@router.callback_query(lambda c: c.data.startswith("ptype_"))
async def vp_add_type(callback: CallbackQuery, state: FSMContext):
    ptype = callback.data.split("_")[1]
    data = await state.get_data()
    vendor = _is_vendor(callback.from_user.id)
    if not vendor:
        await state.clear()
        await callback.answer("Not a vendor")
        return

    allow_preorder = 1 if data["stock"] == 0 else 0

    pid = add_product(
        vendor[0], vendor[2], data["name"], data["description"],
        data["price"], data["stock"], data["category"], ptype, allow_preorder,
    )
    await state.clear()
    await callback.message.edit_text(
        f"Product <b>{data['name']}</b> created (#{pid}).",
        parse_mode="HTML",
        reply_markup=vendor_product_actions(pid),
    )
    await callback.answer()


# --- Edit Product ---

@router.callback_query(lambda c: c.data.startswith("vpedit_"))
async def vp_edit_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    vendor = _is_vendor(callback.from_user.id)
    if not vendor or get_product_owner(product_id) != vendor[0]:
        await callback.answer("Access denied")
        return

    buttons = [
        [InlineKeyboardButton(text="Name", callback_data=f"vpef_name_{product_id}")],
        [InlineKeyboardButton(text="Description", callback_data=f"vpef_description_{product_id}")],
        [InlineKeyboardButton(text="Price", callback_data=f"vpef_price_{product_id}")],
        [InlineKeyboardButton(text="Stock", callback_data=f"vpef_stock_{product_id}")],
        [InlineKeyboardButton(text="Category", callback_data=f"vpef_category_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"vpprod_{product_id}")],
    ]
    await callback.message.edit_text(
        "Select field to edit:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vpef_"))
async def vp_edit_field(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    field = parts[1]
    product_id = int(parts[2])
    vendor = _is_vendor(callback.from_user.id)
    if not vendor or get_product_owner(product_id) != vendor[0]:
        await callback.answer("Access denied")
        return

    await state.update_data(edit_field=field, edit_product_id=product_id)
    await state.set_state(VendorEditProduct.value)
    await callback.message.edit_text(f"Enter new value for {field}:")
    await callback.answer()


@router.message(VendorEditProduct.value)
async def vp_edit_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data["edit_field"]
    product_id = data["edit_product_id"]

    value = message.text
    if field in ("price",):
        try:
            value = float(value)
        except (ValueError, TypeError):
            await message.answer("Invalid number.")
            return
    elif field in ("stock",):
        try:
            value = int(value)
        except (ValueError, TypeError):
            await message.answer("Invalid number.")
            return

    update_product(product_id, **{field: value})
    await state.clear()
    await message.answer(f"Updated {field}.", reply_markup=back_to_menu())


# --- Delete Product ---

@router.callback_query(lambda c: c.data.startswith("vpdel_"))
async def vp_delete(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    vendor = _is_vendor(callback.from_user.id)
    if not vendor or get_product_owner(product_id) != vendor[0]:
        await callback.answer("Access denied")
        return

    delete_product(product_id)
    await callback.message.edit_text("Product deleted.", reply_markup=back_to_menu())
    await callback.answer()


# --- Delivery Items ---

@router.callback_query(lambda c: c.data.startswith("vpdeliv_"))
async def vp_delivery(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    vendor = _is_vendor(callback.from_user.id)
    if not vendor or get_product_owner(product_id) != vendor[0]:
        await callback.answer("Access denied")
        return

    items = get_delivery_items(product_id)
    lines = ["<b>Delivery Items:</b>\n"]
    for item_id, dtype, content, file_id in items:
        preview = (content[:30] + "...") if content and len(content) > 30 else (content or "[media]")
        lines.append(f"  [{dtype}] {preview}")

    if not items:
        lines.append("  No items configured.")

    buttons = [
        [InlineKeyboardButton(text="➕ Add Item", callback_data=f"vpadddeliv_{product_id}")],
        [InlineKeyboardButton(text="🧹 Clear All", callback_data=f"vpcleardeliv_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"vpprod_{product_id}")],
    ]

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vpadddeliv_"))
async def vp_add_delivery(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    await callback.message.edit_text(
        "Select delivery type:",
        reply_markup=delivery_type_keyboard(product_id),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("da_"))
async def vp_delivery_type_selected(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    dtype = parts[1]
    product_id = int(parts[2])

    await state.update_data(da_type=dtype, da_product_id=product_id)

    if dtype in ("photo", "video", "file"):
        await state.set_state(DeliveryAdd.file)
        await callback.message.edit_text(f"Send the {dtype} file:")
    else:
        await state.set_state(DeliveryAdd.content)
        if dtype == "coords":
            await callback.message.edit_text("Enter coordinates (lat, lon):")
        elif dtype == "desc":
            await callback.message.edit_text("Enter description text:")
        else:
            await callback.message.edit_text("Enter text content:")
    await callback.answer()


@router.message(DeliveryAdd.content)
async def vp_delivery_content(message: Message, state: FSMContext):
    data = await state.get_data()
    dtype = data["da_type"]
    product_id = data["da_product_id"]

    actual_type = "coordinates" if dtype == "coords" else ("description" if dtype == "desc" else "text")
    add_delivery_item(product_id, actual_type, message.text)
    await state.clear()
    await message.answer("Delivery item added.", reply_markup=back_to_menu())


@router.message(DeliveryAdd.file)
async def vp_delivery_file(message: Message, state: FSMContext):
    data = await state.get_data()
    dtype = data["da_type"]
    product_id = data["da_product_id"]

    file_id = None
    if dtype == "photo" and message.photo:
        file_id = message.photo[-1].file_id
    elif dtype == "video" and message.video:
        file_id = message.video.file_id
    elif dtype == "file" and message.document:
        file_id = message.document.file_id
    else:
        await message.answer(f"Please send a valid {dtype}.")
        return

    add_delivery_item(product_id, dtype, message.caption or "", file_id)
    await state.clear()
    await message.answer("Delivery item added.", reply_markup=back_to_menu())


@router.callback_query(lambda c: c.data.startswith("vpcleardeliv_"))
async def vp_clear_delivery(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    vendor = _is_vendor(callback.from_user.id)
    if not vendor or get_product_owner(product_id) != vendor[0]:
        await callback.answer("Access denied")
        return

    clear_delivery_items(product_id)
    await callback.message.edit_text("All delivery items cleared.", reply_markup=back_to_menu())
    await callback.answer()


# --- Orders ---

@router.callback_query(lambda c: c.data == "vp_orders")
async def vp_orders(callback: CallbackQuery):
    vendor = _is_vendor(callback.from_user.id)
    if not vendor:
        await callback.answer("Not a vendor")
        return

    orders = get_vendor_orders(vendor[0])
    if not orders:
        await callback.message.edit_text("No orders.", reply_markup=vendor_menu())
        await callback.answer()
        return

    buttons = []
    for o in orders[:20]:
        oid, tid, _, total, status, dtype, _, created = o
        buttons.append([InlineKeyboardButton(
            text=f"#{oid} | {total}$ | {status} | {dtype}",
            callback_data=f"vporder_{oid}",
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="vendor_panel")])

    await callback.message.edit_text(
        "<b>Orders</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vporder_"))
async def vp_order_detail(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[1])
    order = get_order(order_id)
    vendor = _is_vendor(callback.from_user.id)
    if not order or not vendor or order[2] != vendor[0]:
        await callback.answer("Access denied")
        return

    oid, tid, _, total, status, dtype, _, created = order
    text = (
        f"<b>Order #{oid}</b>\n"
        f"Customer: {tid}\n"
        f"Total: {total}$\n"
        f"Status: {status}\n"
        f"Type: {dtype}\n"
        f"Date: {created[:16] if created else '—'}"
    )
    buttons = [[InlineKeyboardButton(text="⬅️ Back", callback_data="vp_orders")]]
    if status == "paid" and dtype == "physical":
        buttons.insert(0, [InlineKeyboardButton(text="✅ Mark Shipped", callback_data=f"vpship_{oid}")])
        buttons.insert(0, [InlineKeyboardButton(text="❌ Cancel (no stock)", callback_data=f"vpcancel_{oid}")])

    await callback.message.edit_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vpship_"))
async def vp_ship(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[1])
    update_order_status(order_id, "shipped")
    await callback.message.edit_text("Marked as shipped.", reply_markup=back_to_menu())
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vpcancel_"))
async def vp_cancel(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[1])
    update_order_status(order_id, "cancelled")
    await callback.message.edit_text("Order cancelled.", reply_markup=back_to_menu())
    await callback.answer()


# --- Tickets ---

@router.callback_query(lambda c: c.data == "vp_tickets")
async def vp_tickets(callback: CallbackQuery):
    vendor = _is_vendor(callback.from_user.id)
    if not vendor:
        await callback.answer("Not a vendor")
        return

    tickets = get_vendor_tickets(vendor[0])
    if not tickets:
        await callback.message.edit_text("No tickets.", reply_markup=vendor_menu())
        await callback.answer()
        return

    buttons = []
    for t_id, order_id, cust_id, subject, status, created in tickets:
        buttons.append([InlineKeyboardButton(
            text=f"#{t_id} [{status}] {subject[:20]}",
            callback_data=f"vptkt_{t_id}",
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="vendor_panel")])

    await callback.message.edit_text(
        "<b>Tickets</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vptkt_"))
async def vp_ticket_detail(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[1])
    ticket = get_ticket(ticket_id)
    vendor = _is_vendor(callback.from_user.id)
    if not ticket or not vendor or ticket[3] != vendor[0]:
        await callback.answer("Access denied")
        return

    messages = get_ticket_messages(ticket_id)
    lines = [f"<b>Ticket #{ticket_id}: {ticket[4]}</b>\nStatus: {ticket[5]}\n"]
    for _, sender_id, msg, created in messages:
        who = "Customer" if sender_id == ticket[2] else "You"
        lines.append(f"<b>{who}</b> ({created[:16]})\n{msg}\n")

    buttons = []
    if ticket[5] != "closed":
        buttons.append([InlineKeyboardButton(text="Reply", callback_data=f"vptktr_{ticket_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="vp_tickets")])

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vptktr_"))
async def vp_ticket_reply(callback: CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.split("_")[1])
    await state.update_data(vp_reply_ticket=ticket_id)
    await state.set_state(VendorTicketReply.message)
    await callback.message.edit_text("Enter your reply:")
    await callback.answer()


@router.message(VendorTicketReply.message)
async def vp_ticket_reply_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket_id = data["vp_reply_ticket"]
    add_ticket_message(ticket_id, message.from_user.id, message.text)
    respond_ticket(ticket_id)
    await state.clear()
    await message.answer("Reply sent.", reply_markup=back_to_menu())


# --- Wallet ---

@router.callback_query(lambda c: c.data == "vp_wallet")
async def vp_wallet(callback: CallbackQuery):
    vendor = _is_vendor(callback.from_user.id)
    if not vendor:
        await callback.answer("Not a vendor")
        return

    balance = get_vendor_wallet_balance(vendor[0])
    buttons = [
        [InlineKeyboardButton(text="💸 Request Withdrawal", callback_data="vp_withdraw")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="vendor_panel")],
    ]
    await callback.message.edit_text(
        f"<b>Vendor Wallet</b>\n\nBalance: {balance:.2f}$",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "vp_withdraw")
async def vp_withdraw(callback: CallbackQuery, state: FSMContext):
    await state.set_state(VendorWithdraw.amount)
    await callback.message.edit_text("Enter withdrawal amount:")
    await callback.answer()


@router.message(VendorWithdraw.amount)
async def vp_withdraw_amount(message: Message, state: FSMContext):
    vendor = _is_vendor(message.from_user.id)
    if not vendor:
        await state.clear()
        await message.answer("Not a vendor.")
        return

    try:
        amount = float(message.text)
    except (ValueError, TypeError):
        await message.answer("Invalid amount.")
        return

    balance = get_vendor_wallet_balance(vendor[0])
    if amount > balance or amount <= 0:
        await message.answer(f"Invalid amount. Available: {balance:.2f}$")
        return

    debit_vendor_wallet(vendor[0], amount)
    request_withdrawal(vendor[0], amount)
    await state.clear()
    await message.answer(
        f"Withdrawal request for {amount}$ submitted. Awaiting admin approval.",
        reply_markup=back_to_menu(),
    )


# --- Reviews ---

@router.callback_query(lambda c: c.data == "vp_reviews")
async def vp_reviews(callback: CallbackQuery):
    vendor = _is_vendor(callback.from_user.id)
    if not vendor:
        await callback.answer("Not a vendor")
        return

    avg, count = get_vendor_rating(vendor[0])
    reviews = get_vendor_reviews(vendor[0])

    lines = [f"<b>Shop Reviews</b>\n\nRating: {'⭐' * int(avg)} {avg}/5 ({count} reviews)\n"]
    for r_id, stars, text, created, username, product_id in reviews:
        line = f"{'⭐' * stars} by @{username or 'anon'}"
        if text:
            line += f" — <i>{text}</i>"
        lines.append(line)

    if not reviews:
        lines.append("No reviews yet.")

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back", callback_data="vendor_panel")],
        ]),
    )
    await callback.answer()


# --- Shop Settings ---

@router.callback_query(lambda c: c.data == "vp_settings")
async def vp_settings(callback: CallbackQuery):
    vendor = _is_vendor(callback.from_user.id)
    if not vendor:
        await callback.answer("Not a vendor")
        return

    buttons = [
        [InlineKeyboardButton(text="Edit Shop Name", callback_data="vpset_name")],
        [InlineKeyboardButton(text="Edit Description", callback_data="vpset_desc")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="vendor_panel")],
    ]
    await callback.message.edit_text(
        f"<b>Shop Settings</b>\n\nName: {vendor[3]}\nDescription: {vendor[4]}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "vpset_name")
async def vpset_name(callback: CallbackQuery, state: FSMContext):
    await state.set_state(VendorSettings.shop_name)
    await callback.message.edit_text("Enter new shop name:")
    await callback.answer()


@router.message(VendorSettings.shop_name)
async def vpset_name_msg(message: Message, state: FSMContext):
    vendor = _is_vendor(message.from_user.id)
    if not vendor:
        await state.clear()
        return
    update_vendor(vendor[0], shop_name=message.text)
    await state.clear()
    await message.answer("Shop name updated.", reply_markup=back_to_menu())


@router.callback_query(lambda c: c.data == "vpset_desc")
async def vpset_desc(callback: CallbackQuery, state: FSMContext):
    await state.set_state(VendorSettings.shop_desc)
    await callback.message.edit_text("Enter new shop description:")
    await callback.answer()


@router.message(VendorSettings.shop_desc)
async def vpset_desc_msg(message: Message, state: FSMContext):
    vendor = _is_vendor(message.from_user.id)
    if not vendor:
        await state.clear()
        return
    update_vendor(vendor[0], shop_description=message.text)
    await state.clear()
    await message.answer("Shop description updated.", reply_markup=back_to_menu())
