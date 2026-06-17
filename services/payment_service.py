from db.database import get_conn


def create_payment(order_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments (order_id, provider, status) VALUES (?, 'internal', 'paid')",
        (order_id,),
    )
    conn.commit()
    conn.close()
