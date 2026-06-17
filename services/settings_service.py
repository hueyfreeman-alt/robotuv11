from db.database import get_conn


def get_setting(key, default=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else default


def set_setting(key, value):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()
    conn.close()


def delete_setting(key):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM settings WHERE key = ?", (key,))
    conn.commit()
    conn.close()
