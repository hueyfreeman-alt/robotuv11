from aiogram import Bot
from db.database import get_conn


def get_delivery_items(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, delivery_type, content, file_id FROM product_delivery WHERE product_id = ? ORDER BY sort_order",
        (product_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def add_delivery_item(product_id, delivery_type, content, file_id=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM product_delivery WHERE product_id = ?",
        (product_id,),
    )
    next_order = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO product_delivery (product_id, delivery_type, content, file_id, sort_order) VALUES (?, ?, ?, ?, ?)",
        (product_id, delivery_type, content, file_id, next_order),
    )
    conn.commit()
    conn.close()


def clear_delivery_items(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM product_delivery WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()


def delete_delivery_item(item_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM product_delivery WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


async def deliver_digital(bot: Bot, user_id: int, product_ids: list):
    """Deliver all configured digital items for the given product IDs."""
    for product_id in product_ids:
        items = get_delivery_items(product_id)
        if not items:
            continue

        for item_id, delivery_type, content, file_id in items:
            if delivery_type == "text":
                await bot.send_message(user_id, content, parse_mode="HTML")
            elif delivery_type == "description":
                await bot.send_message(user_id, f"<i>{content}</i>", parse_mode="HTML")
            elif delivery_type == "photo":
                if file_id:
                    await bot.send_photo(user_id, file_id, caption=content or None)
                elif content:
                    await bot.send_message(user_id, content)
            elif delivery_type == "video":
                if file_id:
                    await bot.send_video(user_id, file_id, caption=content or None)
                elif content:
                    await bot.send_message(user_id, content)
            elif delivery_type == "file":
                if file_id:
                    await bot.send_document(user_id, file_id, caption=content or None)
                elif content:
                    await bot.send_message(user_id, content)
            elif delivery_type == "coordinates":
                try:
                    lat, lon = content.split(",")
                    await bot.send_location(user_id, float(lat.strip()), float(lon.strip()))
                except (ValueError, AttributeError):
                    await bot.send_message(user_id, f"Location: {content}")
