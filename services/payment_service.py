from db.database import get_conn


def create_payment(order_id, total):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments (order_id, provider, status) VALUES (?, ?, ?)",
        (order_id, "internal", "paid"),
    )
    conn.commit()
    conn.close()
