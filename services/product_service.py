from db.database import get_conn


def get_all_products():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock, category, type FROM products")
    rows = cur.fetchall()
    conn.close()
    return rows


def decrease_stock(product_id, quantity):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE products SET stock = stock - ? WHERE id = ?",
        (quantity, product_id),
    )
    conn.commit()
    conn.close()
