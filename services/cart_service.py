from db.database import get_cursor


def add_to_cart(telegram_id, product_id, quantity):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, quantity FROM cart"
            " WHERE telegram_id = ? AND product_id = ?",
            (telegram_id, product_id),
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE cart SET quantity = quantity + ?"
                " WHERE id = ?",
                (quantity, row[0]),
            )
        else:
            cur.execute(
                "INSERT INTO cart"
                " (telegram_id, product_id, quantity)"
                " VALUES (?, ?, ?)",
                (telegram_id, product_id, quantity),
            )


def get_cart(telegram_id):
    with get_cursor() as cur:
        cur.execute(
            """SELECT p.name, p.price, c.quantity
               FROM cart c JOIN products p ON c.product_id = p.id
               WHERE c.telegram_id = ?""",
            (telegram_id,),
        )
        return cur.fetchall()


def get_cart_raw(telegram_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT product_id, quantity"
            " FROM cart WHERE telegram_id = ?",
            (telegram_id,),
        )
        return cur.fetchall()


def clear_cart(telegram_id):
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM cart WHERE telegram_id = ?",
            (telegram_id,),
        )


def compute_cart_total(items):
    return sum(price * qty for _, price, qty in items)
