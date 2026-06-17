from db.database import get_cursor


def create_order(telegram_id, total, order_type):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO orders"
            " (telegram_id, total, status, type)"
            " VALUES (?, ?, 'pending', ?)",
            (telegram_id, total, order_type),
        )
        return cur.lastrowid


def add_order_items(order_id, items):
    with get_cursor() as cur:
        for product_id, quantity in items:
            cur.execute(
                "INSERT INTO order_items"
                " (order_id, product_id, quantity)"
                " VALUES (?, ?, ?)",
                (order_id, product_id, quantity),
            )


def update_order_status(order_id, status):
    with get_cursor() as cur:
        cur.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id),
        )


def get_order(order_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,),
        )
        return cur.fetchone()
