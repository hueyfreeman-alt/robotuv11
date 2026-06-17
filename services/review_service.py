from db.database import get_conn


def add_review(order_id, product_id, vendor_id, customer_id, stars, text=""):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO reviews (order_id, product_id, vendor_id, customer_id, stars, text)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (order_id, product_id, vendor_id, customer_id, stars, text),
    )
    conn.commit()
    conn.close()


def get_product_reviews(product_id, limit=10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT r.id, r.stars, r.text, r.created_at, u.username
           FROM reviews r LEFT JOIN users u ON r.customer_id = u.telegram_id
           WHERE r.product_id = ?
           ORDER BY r.created_at DESC LIMIT ?""",
        (product_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_vendor_reviews(vendor_id, limit=10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT r.id, r.stars, r.text, r.created_at, u.username, r.product_id
           FROM reviews r LEFT JOIN users u ON r.customer_id = u.telegram_id
           WHERE r.vendor_id = ?
           ORDER BY r.created_at DESC LIMIT ?""",
        (vendor_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_product_rating(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT AVG(stars), COUNT(*) FROM reviews WHERE product_id = ?",
        (product_id,),
    )
    row = cur.fetchone()
    conn.close()
    avg = round(row[0], 1) if row[0] else 0.0
    count = row[1] if row[1] else 0
    return avg, count


def get_vendor_rating(vendor_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT AVG(stars), COUNT(*) FROM reviews WHERE vendor_id = ?",
        (vendor_id,),
    )
    row = cur.fetchone()
    conn.close()
    avg = round(row[0], 1) if row[0] else 0.0
    count = row[1] if row[1] else 0
    return avg, count


def has_reviewed_order(order_id, customer_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM reviews WHERE order_id = ? AND customer_id = ?",
        (order_id, customer_id),
    )
    count = cur.fetchone()[0]
    conn.close()
    return count > 0
