from db.database import get_conn


def register_user(telegram_id, username=""):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
        (telegram_id, username),
    )
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT telegram_id FROM users")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_user_count():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count
