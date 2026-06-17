from db.database import get_conn


def add_to_cart(telegram_id, product_id, quantity):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, quantity FROM cart WHERE telegram_id = ? AND product_id = ?",
        (telegram_id, product_id),
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE cart SET quantity = quantity + ? WHERE id = ?",
            (quantity, row[0]),
        )
    else:
        cur.execute(
            "INSERT INTO cart (telegram_id, product_id, quantity) VALUES (?, ?, ?)",
            (telegram_id, product_id, quantity),
        )
    conn.commit()
    conn.close()


def get_cart(telegram_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.name, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.telegram_id = ?
        """,
        (telegram_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_cart_raw(telegram_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT product_id, quantity FROM cart WHERE telegram_id = ?",
        (telegram_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def clear_cart(telegram_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()
