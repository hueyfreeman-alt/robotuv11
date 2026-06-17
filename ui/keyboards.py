from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Shop", callback_data="shop")],
        [InlineKeyboardButton(text="🛒 Cart", callback_data="cart")],
        [InlineKeyboardButton(text="ℹ️ Help", callback_data="help")],
    ])


def back_to_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_menu")],
    ])


def category_keyboard(categories):
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=f"📂 {cat}", callback_data=f"cat_{cat}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_actions(product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add to Cart", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="shop")],
    ])


def cart_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Checkout", callback_data="checkout")],
        [InlineKeyboardButton(text="🧹 Clear Cart", callback_data="clear_cart")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_menu")],
    ])


def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Products", callback_data="adm_products")],
        [InlineKeyboardButton(text="🚀 Delivery", callback_data="adm_delivery")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="adm_broadcast")],
        [InlineKeyboardButton(text="🎬 Promo Media", callback_data="adm_promo")],
        [InlineKeyboardButton(text="📊 Stats", callback_data="adm_stats")],
    ])


def vendor_product_actions(product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Edit", callback_data=f"vedit_{product_id}")],
        [InlineKeyboardButton(text="📦 Delivery Items", callback_data=f"vdeliv_{product_id}")],
        [InlineKeyboardButton(text="🗑 Delete", callback_data=f"vdel_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="adm_products")],
    ])


def delivery_type_keyboard(product_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Text", callback_data=f"dadd_text_{product_id}")],
        [InlineKeyboardButton(text="🖼 Photo", callback_data=f"dadd_photo_{product_id}")],
        [InlineKeyboardButton(text="🎬 Video", callback_data=f"dadd_video_{product_id}")],
        [InlineKeyboardButton(text="📁 File", callback_data=f"dadd_file_{product_id}")],
        [InlineKeyboardButton(text="📍 Coordinates", callback_data=f"dadd_coords_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"vdeliv_{product_id}")],
    ])


def broadcast_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 Photo", callback_data="bc_photo")],
        [InlineKeyboardButton(text="🎬 Video", callback_data="bc_video")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_panel")],
    ])


def confirm_keyboard(action):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm_{action}"),
            InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_{action}"),
        ],
    ])
