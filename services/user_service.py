import logging
import sqlite3

from db.database import get_conn

logger = logging.getLogger(__name__)


def register_user(telegram_id, username=""):
    """Register a user (no-op if already exists). Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
                (telegram_id, username),
            )
            conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to register user %d: %s", telegram_id, e)
        raise


def get_all_users():
    """Fetch all user telegram IDs. Returns empty list on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT telegram_id FROM users")
            return [r[0] for r in cur.fetchall()]
    except sqlite3.Error as e:
        logger.error("Failed to fetch all users: %s", e)
        return []


def get_user_count():
    """Get total user count. Returns 0 on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            return cur.fetchone()[0]
    except sqlite3.Error as e:
        logger.error("Failed to get user count: %s", e)
        return 0
