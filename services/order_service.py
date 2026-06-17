from db.database import get_conn


def create_order(telegram_id, total, order_type):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (telegram_id, total, status, type) VALUES (?, ?, 'pending', ?)",
        (telegram_id, total, order_type),
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


def update_order_status(order_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()


def get_order(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()
    return row
