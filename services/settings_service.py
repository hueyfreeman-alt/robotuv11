from db.database import get_cursor


def get_setting(key, default=None):
    with get_cursor() as cur:
        cur.execute(
            "SELECT value FROM settings WHERE key = ?",
            (key,),
        )
        row = cur.fetchone()
        return row[0] if row else default


def set_setting(key, value):
    with get_cursor() as cur:
        cur.execute(
            "INSERT OR REPLACE INTO settings"
            " (key, value) VALUES (?, ?)",
            (key, value),
        )


def delete_setting(key):
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM settings WHERE key = ?",
            (key,),
        )
