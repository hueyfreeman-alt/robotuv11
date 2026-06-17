import logging
import sqlite3

from db.database import get_conn

logger = logging.getLogger(__name__)


def add_to_cart(telegram_id: int, product_id: int, quantity: int):
    """Add item to cart (upserts if already present). Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, quantity FROM cart WHERE telegram_id = ? AND product_id = ?",
                (telegram_id, product_id),
            )
            row = cur.fetchone()
            if row:
                cur.execute(
                    "UPDATE cart SET quantity = quantity + ? WHERE id = ?",
                    (quantity, row[0]),
                )
            else:
                cur.execute(
                    "INSERT INTO cart (telegram_id, product_id, quantity) VALUES (?, ?, ?)",
                    (telegram_id, product_id, quantity),
                )
            conn.commit()
    except sqlite3.Error as e:
        logger.error(
            "Failed to add product %d to cart for user %d: %s",
            product_id, telegram_id, e,
        )
        raise


def get_cart(telegram_id: int):
    """Get cart items with product details. Returns empty list on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """SELECT p.name, p.price, c.quantity
                   FROM cart c JOIN products p ON c.product_id = p.id
                   WHERE c.telegram_id = ?""",
                (telegram_id,),
            )
            return cur.fetchall()
    except sqlite3.Error as e:
        logger.error("Failed to fetch cart for user %d: %s", telegram_id, e)
        return []


def get_cart_raw(telegram_id: int):
    """Get raw cart entries (product_id, quantity). Returns empty list on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT product_id, quantity FROM cart WHERE telegram_id = ?",
                (telegram_id,),
            )
            return cur.fetchall()
    except sqlite3.Error as e:
        logger.error("Failed to fetch raw cart for user %d: %s", telegram_id, e)
        return []


def clear_cart(telegram_id: int):
    """Clear user's cart. Raises on failure so callers know it wasn't cleared."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM cart WHERE telegram_id = ?", (telegram_id,)
            )
            conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to clear cart for user %d: %s", telegram_id, e)
        raise
