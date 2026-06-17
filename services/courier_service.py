from db.database import get_conn


def create_courier_order(order_id, customer_id, vendor_id, delivery_address):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO courier_orders (order_id, customer_id, vendor_id, delivery_address)
           VALUES (?, ?, ?, ?)""",
        (order_id, customer_id, vendor_id, delivery_address),
    )
    co_id = cur.lastrowid
    conn.commit()
    conn.close()
    return co_id


def get_courier_order(courier_order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, order_id, customer_id, vendor_id, delivery_address, status, created_at FROM courier_orders WHERE id = ?",
        (courier_order_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_vendor_courier_orders(vendor_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT co.id, co.order_id, co.customer_id, co.delivery_address, co.status, co.created_at
           FROM courier_orders co WHERE co.vendor_id = ?
           ORDER BY co.created_at DESC""",
        (vendor_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def update_courier_status(courier_order_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE courier_orders SET status = ? WHERE id = ?",
        (status, courier_order_id),
    )
    conn.commit()
    conn.close()
