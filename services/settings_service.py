import logging
import sqlite3

from db.database import get_conn

logger = logging.getLogger(__name__)


def get_setting(key, default=None):
    """Fetch a setting value. Returns default on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else default
    except sqlite3.Error as e:
        logger.error("Failed to get setting %r: %s", key, e)
        return default


def set_setting(key, value):
    """Set a setting value. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
            conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to set setting %r: %s", key, e)
        raise


def delete_setting(key):
    """Delete a setting. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM settings WHERE key = ?", (key,))
            conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to delete setting %r: %s", key, e)
        raise
