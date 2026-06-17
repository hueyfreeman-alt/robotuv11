import logging
import sqlite3

from db.database import get_conn

logger = logging.getLogger(__name__)


def create_order(telegram_id: int, total: float, order_type: str) -> int:
    """Create an order and return its ID. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO orders (telegram_id, total, status, type) VALUES (?, ?, ?, ?)",
                (telegram_id, total, "pending", order_type),
            )
            conn.commit()
            order_id = cur.lastrowid
            if order_id is None:
                raise RuntimeError("Failed to retrieve order ID after insert")
            return order_id
    except sqlite3.Error as e:
        logger.error(
            "Failed to create order for user %d (total=%.2f): %s",
            telegram_id, total, e,
        )
        raise


def add_order_items(order_id: int, items: list[tuple[int, int]]):
    """Add items to an order. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            for product_id, quantity in items:
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                    (order_id, product_id, quantity),
                )
            conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to add items to order %d: %s", order_id, e)
        raise


def update_order_status(order_id: int, status: str):
    """Update order status. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE orders SET status = ? WHERE id = ?",
                (status, order_id),
            )
            if cur.rowcount == 0:
                raise ValueError(f"Order {order_id} not found")
            conn.commit()
    except sqlite3.Error as e:
        logger.error(
            "Failed to update order %d to status %r: %s", order_id, status, e
        )
        raise


def get_order(order_id: int):
    """Fetch an order by ID. Returns None on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            return cur.fetchone()
    except sqlite3.Error as e:
        logger.error("Failed to fetch order %d: %s", order_id, e)
        return None
