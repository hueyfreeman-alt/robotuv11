from db.database import get_conn


def create_order(telegram_id, total, order_type):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (telegram_id, total, status, type) VALUES (?, ?, ?, ?)",
        (telegram_id, total, "pending", order_type),
    )
    conn.commit()
    order_id = cur.lastrowid
    conn.close()
    return order_id


def add_order_items(order_id, raw_items):
    conn = get_conn()
    cur = conn.cursor()
    for product_id, quantity in raw_items:
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
            (order_id, product_id, quantity),
        )
    conn.commit()
    conn.close()
