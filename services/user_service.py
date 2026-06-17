from db.database import get_cursor


def register_user(telegram_id, username=""):
    with get_cursor() as cur:
        cur.execute(
            "INSERT OR IGNORE INTO users"
            " (telegram_id, username) VALUES (?, ?)",
            (telegram_id, username),
        )


def get_all_users():
    with get_cursor() as cur:
        cur.execute("SELECT telegram_id FROM users")
        return [r[0] for r in cur.fetchall()]


def get_user_count():
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]
