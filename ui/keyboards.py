from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# --- Main Menu ---

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Shop Now", callback_data="shop")],
        [
            InlineKeyboardButton(text="👤 Profile", callback_data="profile"),
            InlineKeyboardButton(text="💰 Deposit", callback_data="deposit"),
        ],
        [InlineKeyboardButton(text="📦 Courier", callback_data="courier")],
        [
            InlineKeyboardButton(text="📖 Guide", callback_data="help_guide"),
            InlineKeyboardButton(text="📜 Rules", callback_data="help_rules"),
        ],
    ])


def back_to_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_menu")],
    ])


# --- Shop Navigation ---

def city_keyboard(cities):
    buttons = []
    for city_id, name, _ in cities:
        buttons.append([InlineKeyboardButton(text=f"🏙 {name}", callback_data=f"city_{city_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def vendor_keyboard(vendors):
    buttons = []
    for v in vendors:
        vid, _, _, shop_name, _, _, _ = v
        buttons.append([InlineKeyboardButton(text=f"🏪 {shop_name}", callback_data=f"vendor_{vid}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="shop")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_card_keyboard(product_id, has_stock, allow_preorder):
    buttons = []
    if has_stock:
        buttons.append([InlineKeyboardButton(text="🛒 Add to Cart", callback_data=f"add_{product_id}")])
    elif allow_preorder:
        buttons.append([InlineKeyboardButton(text="📋 Preorder", callback_data=f"preorder_{product_id}")])
    buttons.append([InlineKeyboardButton(text="⭐ Reviews", callback_data=f"rev_{product_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Cart ---

def cart_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Checkout", callback_data="checkout")],
        [InlineKeyboardButton(text="🧹 Clear Cart", callback_data="clear_cart")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_menu")],
    ])


# --- Profile ---

def profile_keyboard(is_vendor=False):
    buttons = [
        [InlineKeyboardButton(text="📋 My Orders", callback_data="my_orders")],
        [InlineKeyboardButton(text="🎫 My Tickets", callback_data="my_tickets")],
        [InlineKeyboardButton(text="🛒 My Cart", callback_data="cart")],
    ]
    if is_vendor:
        buttons.append([InlineKeyboardButton(text="🏪 Vendor Panel", callback_data="vendor_panel")])
    else:
        buttons.append([InlineKeyboardButton(text="⬆️ Upgrade (Become Vendor)", callback_data="upgrade_vendor")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Deposit ---

def deposit_amounts():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="10$", callback_data="dep_10"),
            InlineKeyboardButton(text="25$", callback_data="dep_25"),
            InlineKeyboardButton(text="50$", callback_data="dep_50"),
        ],
        [
            InlineKeyboardButton(text="100$", callback_data="dep_100"),
            InlineKeyboardButton(text="250$", callback_data="dep_250"),
        ],
        [InlineKeyboardButton(text="Custom Amount", callback_data="dep_custom")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_menu")],
    ])


# --- Admin ---

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏙 Cities", callback_data="adm_cities")],
        [InlineKeyboardButton(text="🏪 Vendors", callback_data="adm_vendors")],
        [InlineKeyboardButton(text="💸 Withdrawals", callback_data="adm_withdrawals")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="🎬 Promo Media", callback_data="adm_promo")],
        [InlineKeyboardButton(text="📊 Stats", callback_data="adm_stats")],
    ])


# --- Vendor Panel ---

def vendor_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Products", callback_data="vp_products")],
        [InlineKeyboardButton(text="📋 Orders", callback_data="vp_orders")],
        [InlineKeyboardButton(text="🎫 Tickets", callback_data="vp_tickets")],
        [InlineKeyboardButton(text="💰 Wallet", callback_data="vp_wallet")],
        [InlineKeyboardButton(text="⭐ Reviews", callback_data="vp_reviews")],
        [InlineKeyboardButton(text="⚙️ Shop Settings", callback_data="vp_settings")],
    ])


def vendor_product_actions(product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Edit", callback_data=f"vpedit_{product_id}")],
        [InlineKeyboardButton(text="📦 Delivery Items", callback_data=f"vpdeliv_{product_id}")],
        [InlineKeyboardButton(text="🗑 Delete", callback_data=f"vpdel_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="vp_products")],
    ])


def delivery_type_keyboard(product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Text", callback_data=f"da_text_{product_id}")],
        [InlineKeyboardButton(text="📄 Description", callback_data=f"da_desc_{product_id}")],
        [InlineKeyboardButton(text="🖼 Photo", callback_data=f"da_photo_{product_id}")],
        [InlineKeyboardButton(text="🎬 Video", callback_data=f"da_video_{product_id}")],
        [InlineKeyboardButton(text="📁 File", callback_data=f"da_file_{product_id}")],
        [InlineKeyboardButton(text="📍 Coordinates", callback_data=f"da_coords_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"vpdeliv_{product_id}")],
    ])


def broadcast_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 Photo", callback_data="bc_photo")],
        [InlineKeyboardButton(text="🎬 Video", callback_data="bc_video")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")],
    ])


# --- Reviews ---

def stars_keyboard(order_id, product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐", callback_data=f"star_1_{order_id}_{product_id}"),
            InlineKeyboardButton(text="⭐⭐", callback_data=f"star_2_{order_id}_{product_id}"),
            InlineKeyboardButton(text="⭐⭐⭐", callback_data=f"star_3_{order_id}_{product_id}"),
        ],
        [
            InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data=f"star_4_{order_id}_{product_id}"),
            InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data=f"star_5_{order_id}_{product_id}"),
        ],
    ])


# --- Orders ---

def order_actions(order_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Review", callback_data=f"review_{order_id}")],
        [InlineKeyboardButton(text="🎫 Open Ticket", callback_data=f"ticket_{order_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="my_orders")],
    ])
