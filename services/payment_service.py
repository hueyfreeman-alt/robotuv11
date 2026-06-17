from db.database import get_conn


def create_payment(order_id, amount, provider="oxapay", status="pending"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments (order_id, provider, status) VALUES (?, ?, ?)",
        (order_id, provider, status),
    )
    conn.commit()
    conn.close()
