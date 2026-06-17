from aiogram import Bot
from db.database import get_cursor


def get_delivery_items(product_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT delivery_type, content, file_id"
            " FROM product_delivery"
            " WHERE product_id = ? ORDER BY sort_order",
            (product_id,),
        )
        return cur.fetchall()


def add_delivery_item(product_id, delivery_type, content, file_id=None):
    with get_cursor() as cur:
        cur.execute(
            "SELECT COALESCE(MAX(sort_order), 0) + 1"
            " FROM product_delivery WHERE product_id = ?",
            (product_id,),
        )
        next_order = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO product_delivery"
            " (product_id, delivery_type, content,"
            " file_id, sort_order)"
            " VALUES (?, ?, ?, ?, ?)",
            (product_id, delivery_type, content,
             file_id, next_order),
        )


def clear_delivery_items(product_id):
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM product_delivery"
            " WHERE product_id = ?",
            (product_id,),
        )


def delete_delivery_item(item_id):
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM product_delivery WHERE id = ?",
            (item_id,),
        )


async def _send_delivery_item(bot, user_id, delivery_type,
                              content, file_id):
    if delivery_type == "text":
        await bot.send_message(
            user_id, f"📝{content}", parse_mode="HTML",
        )
    elif delivery_type == "photo":
        if file_id:
            await bot.send_photo(
                user_id, file_id, caption=content or None,
            )
        else:
            await bot.send_message(user_id, f"🖼 {content}")
    elif delivery_type == "video":
        if file_id:
            await bot.send_video(
                user_id, file_id, caption=content or None,
            )
        else:
            await bot.send_message(user_id, f"🎬{content}")
    elif delivery_type == "file":
        if file_id:
            await bot.send_document(
                user_id, file_id, caption=content or None,
            )
        else:
            await bot.send_message(user_id, f"📁{content}")
    elif delivery_type == "coordinates":
        try:
            lat, lon = content.split(",")
            await bot.send_location(
                user_id, float(lat.strip()), float(lon.strip()),
            )
        except (ValueError, AttributeError):
            await bot.send_message(user_id, f"📍{content}")


async def _deliver_products(bot, user_id, product_ids):
    for product_id in product_ids:
        items = get_delivery_items(product_id)
        if not items:
            continue

        await bot.send_message(
            user_id,
            "📦<b>Digital Delivery:</b>",
            parse_mode="HTML",
        )

        for delivery_type, content, file_id in items:
            await _send_delivery_item(
                bot, user_id, delivery_type, content, file_id,
            )


async def deliver(bot: Bot, user_id: int, cart_items):
    """Deliver all digital content for purchased products."""
    with get_cursor() as cur:
        cur.execute(
            """SELECT DISTINCT c.product_id
               FROM cart c JOIN products p ON c.product_id = p.id
               WHERE c.telegram_id = ?""",
            (user_id,),
        )
        product_ids_from_cart = cur.fetchall()

        if not product_ids_from_cart:
            for name, _, _ in cart_items:
                cur.execute(
                    "SELECT id FROM products WHERE name = ?",
                    (name,),
                )
                row = cur.fetchone()
                if row:
                    product_ids_from_cart.append((row[0],))

    pids = [pid for (pid,) in product_ids_from_cart]
    await _deliver_products(bot, user_id, pids)


async def deliver_by_product_ids(bot: Bot, user_id: int,
                                 product_ids):
    """Deliver digital content for specific product IDs."""
    await _deliver_products(bot, user_id, product_ids)
