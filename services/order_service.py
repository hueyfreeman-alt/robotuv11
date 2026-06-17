from db.database import get_conn


def create_order(telegram_id, vendor_id, total, delivery_type="digital"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (telegram_id, vendor_id, total, status, delivery_type) VALUES (?, ?, ?, 'paid', ?)",
        (telegram_id, vendor_id, total, delivery_type),
    )
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id


def add_order_items(order_id, items):
    conn = get_conn()
    cur = conn.cursor()
    for product_id, quantity in items:
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
            (order_id, product_id, quantity),
        )
    conn.commit()
    conn.close()


def get_order(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, telegram_id, vendor_id, total, status, delivery_type, reviewed, created_at FROM orders WHERE id = ?",
        (order_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_user_orders(telegram_id, limit=20):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, telegram_id, vendor_id, total, status, delivery_type, reviewed, created_at FROM orders WHERE telegram_id = ? ORDER BY created_at DESC LIMIT ?",
        (telegram_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_vendor_orders(vendor_id, limit=50):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, telegram_id, vendor_id, total, status, delivery_type, reviewed, created_at FROM orders WHERE vendor_id = ? ORDER BY created_at DESC LIMIT ?",
        (vendor_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def update_order_status(order_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()


def mark_order_reviewed(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET reviewed = 1 WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()


def get_order_items(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT oi.product_id, oi.quantity, p.name, p.price
           FROM order_items oi JOIN products p ON oi.product_id = p.id
           WHERE oi.order_id = ?""",
        (order_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows
