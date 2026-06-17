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


def get_user(telegram_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT telegram_id, username, balance, role, joined_at FROM users WHERE telegram_id = ?",
        (telegram_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_balance(telegram_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0.0


def add_balance(telegram_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET balance = balance + ? WHERE telegram_id = ?",
        (amount, telegram_id),
    )
    conn.commit()
    conn.close()


def deduct_balance(telegram_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET balance = balance - ? WHERE telegram_id = ?",
        (amount, telegram_id),
    )
    conn.commit()
    conn.close()


def set_role(telegram_id, role):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET role = ? WHERE telegram_id = ?",
        (role, telegram_id),
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
