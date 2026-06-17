import logging
import sqlite3

from aiogram import Bot
from db.database import get_conn

logger = logging.getLogger(__name__)


def get_delivery_items(product_id):
    """Fetch delivery items for a product. Returns empty list on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT delivery_type, content, file_id FROM product_delivery WHERE product_id = ? ORDER BY sort_order",
                (product_id,),
            )
            return cur.fetchall()
    except sqlite3.Error as e:
        logger.error("Failed to fetch delivery items for product %d: %s", product_id, e)
        return []


def add_delivery_item(product_id, delivery_type, content, file_id=None):
    """Add a delivery item. Raises on failure."""
    try:
        with get_conn() as conn:
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
    except sqlite3.Error as e:
        logger.error("Failed to add delivery item for product %d: %s", product_id, e)
        raise


def clear_delivery_items(product_id):
    """Clear all delivery items for a product. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM product_delivery WHERE product_id = ?", (product_id,))
            conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to clear delivery items for product %d: %s", product_id, e)
        raise


def delete_delivery_item(item_id):
    """Delete a single delivery item. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM product_delivery WHERE id = ?", (item_id,))
            conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to delete delivery item %d: %s", item_id, e)
        raise


async def _send_delivery_item(bot: Bot, user_id: int, delivery_type: str, content: str, file_id: str):
    """Send a single delivery item to the user."""
    if delivery_type == "text":
        await bot.send_message(user_id, f"📝 {content}", parse_mode="HTML")
    elif delivery_type == "photo":
        if file_id:
            await bot.send_photo(user_id, file_id, caption=content or None)
        else:
            await bot.send_message(user_id, f"🖼 {content}")
    elif delivery_type == "video":
        if file_id:
            await bot.send_video(user_id, file_id, caption=content or None)
        else:
            await bot.send_message(user_id, f"🎬 {content}")
    elif delivery_type == "file":
        if file_id:
            await bot.send_document(user_id, file_id, caption=content or None)
        else:
            await bot.send_message(user_id, f"📁 {content}")
    elif delivery_type == "coordinates":
        try:
            lat, lon = content.split(",")
            await bot.send_location(user_id, float(lat.strip()), float(lon.strip()))
        except (ValueError, AttributeError):
            await bot.send_message(user_id, f"📍 {content}")


async def deliver(bot: Bot, user_id: int, cart_items):
    """Deliver all digital content for purchased products."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()

            cur.execute(
                """SELECT DISTINCT c.product_id
                   FROM cart c JOIN products p ON c.product_id = p.id
                   WHERE c.telegram_id = ?""",
                (user_id,),
            )
            product_ids_from_cart = cur.fetchall()

            # If cart already cleared, look up by product names
            if not product_ids_from_cart:
                for name, _, _ in cart_items:
                    cur.execute("SELECT id FROM products WHERE name = ?", (name,))
                    row = cur.fetchone()
                    if row:
                        product_ids_from_cart.append((row[0],))
    except sqlite3.Error as e:
        logger.error("Failed to look up product IDs for delivery to user %d: %s", user_id, e)
        raise

    for (product_id,) in product_ids_from_cart:
        items = get_delivery_items(product_id)
        if not items:
            continue

        try:
            await bot.send_message(user_id, "📦 <b>Digital Delivery:</b>", parse_mode="HTML")
            for delivery_type, content, file_id in items:
                await _send_delivery_item(bot, user_id, delivery_type, content, file_id)
        except Exception as e:
            logger.error(
                "Failed to deliver product %d to user %d: %s", product_id, user_id, e
            )
            raise


async def deliver_by_product_ids(bot: Bot, user_id: int, product_ids):
    """Deliver digital content for specific product IDs."""
    for product_id in product_ids:
        items = get_delivery_items(product_id)
        if not items:
            continue

        try:
            await bot.send_message(user_id, "📦 <b>Digital Delivery:</b>", parse_mode="HTML")
            for delivery_type, content, file_id in items:
                await _send_delivery_item(bot, user_id, delivery_type, content, file_id)
        except Exception as e:
            logger.error(
                "Failed to deliver product %d to user %d: %s", product_id, user_id, e
            )
            raise
