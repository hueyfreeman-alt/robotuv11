from db.database import get_conn


def create_vendor(telegram_id, city_id, shop_name, shop_description=""):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO vendors (telegram_id, city_id, shop_name, shop_description)
           VALUES (?, ?, ?, ?)""",
        (telegram_id, city_id, shop_name, shop_description),
    )
    vendor_id = cur.lastrowid
    conn.commit()
    conn.close()
    return vendor_id


def get_vendor_by_telegram(telegram_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, telegram_id, city_id, shop_name, shop_description, is_active, wallet_balance FROM vendors WHERE telegram_id = ?",
        (telegram_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_vendor(vendor_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, telegram_id, city_id, shop_name, shop_description, is_active, wallet_balance FROM vendors WHERE id = ?",
        (vendor_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_vendors_by_city(city_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, telegram_id, city_id, shop_name, shop_description, is_active, wallet_balance FROM vendors WHERE city_id = ? AND is_active = 1",
        (city_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_vendors():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, telegram_id, city_id, shop_name, shop_description, is_active, wallet_balance FROM vendors"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def update_vendor(vendor_id, **kwargs):
    conn = get_conn()
    cur = conn.cursor()
    for key, value in kwargs.items():
        cur.execute(f"UPDATE vendors SET {key} = ? WHERE id = ?", (value, vendor_id))
    conn.commit()
    conn.close()


def credit_vendor_wallet(vendor_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE vendors SET wallet_balance = wallet_balance + ? WHERE id = ?",
        (amount, vendor_id),
    )
    conn.commit()
    conn.close()


def debit_vendor_wallet(vendor_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE vendors SET wallet_balance = wallet_balance - ? WHERE id = ?",
        (amount, vendor_id),
    )
    conn.commit()
    conn.close()


def get_vendor_wallet_balance(vendor_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT wallet_balance FROM vendors WHERE id = ?", (vendor_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0.0


# --- City management ---

def create_city(name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO cities (name) VALUES (?)", (name,))
    city_id = cur.lastrowid
    conn.commit()
    conn.close()
    return city_id


def get_all_cities():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, is_active FROM cities WHERE is_active = 1")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_city(city_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, is_active FROM cities WHERE id = ?", (city_id,))
    row = cur.fetchone()
    conn.close()
    return row


def delete_city(city_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE cities SET is_active = 0 WHERE id = ?", (city_id,))
    conn.commit()
    conn.close()


# --- Withdrawals ---

def request_withdrawal(vendor_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO withdrawals (vendor_id, amount) VALUES (?, ?)",
        (vendor_id, amount),
    )
    w_id = cur.lastrowid
    conn.commit()
    conn.close()
    return w_id


def get_pending_withdrawals():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT w.id, w.vendor_id, w.amount, w.created_at, v.shop_name
           FROM withdrawals w JOIN vendors v ON w.vendor_id = v.id
           WHERE w.status = 'pending'"""
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def update_withdrawal_status(withdrawal_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE withdrawals SET status = ? WHERE id = ?",
        (status, withdrawal_id),
    )
    conn.commit()
    conn.close()
