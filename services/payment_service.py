from db.database import get_cursor


def create_payment(order_id, amount):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO payments"
            " (order_id, provider, status)"
            " VALUES (?, 'internal', 'paid')",
            (order_id,),
        )
