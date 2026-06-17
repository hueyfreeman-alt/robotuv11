import logging
import sqlite3

from db.database import get_conn

logger = logging.getLogger(__name__)


def create_payment(order_id: int, amount: float):
    """Record a payment for an order. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO payments (order_id, provider, status) VALUES (?, 'internal', 'paid')",
                (order_id,),
            )
            conn.commit()
            logger.info(
                "Payment created for order %d (amount=%.2f)", order_id, amount
            )
    except sqlite3.Error as e:
        logger.error(
            "Failed to create payment for order %d (amount=%.2f): %s",
            order_id, amount, e,
        )
        raise
