import logging
import sqlite3

from db.database import get_conn

logger = logging.getLogger(__name__)


def save_broadcast(media_type, file_id, caption=""):
    """Save a broadcast record. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO broadcasts (media_type, file_id, caption) VALUES (?, ?, ?)",
                (media_type, file_id, caption),
            )
            conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to save broadcast: %s", e)
        raise


def get_broadcasts(limit=10):
    """Fetch recent broadcasts. Returns empty list on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, media_type, file_id, caption, sent_at FROM broadcasts ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return cur.fetchall()
    except sqlite3.Error as e:
        logger.error("Failed to fetch broadcasts: %s", e)
        return []
