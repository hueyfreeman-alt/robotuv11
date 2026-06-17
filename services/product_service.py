from db.database import get_conn


def get_all_products():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock, category, type FROM products WHERE stock > 0")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_product(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, description, price, stock, category, type FROM products WHERE id = ?",
        (product_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_products_by_category(category):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, price, stock, category, type FROM products WHERE category = ? AND stock > 0",
        (category,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_categories():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM products WHERE stock > 0")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]


def add_product(name, description, price, stock, category, ptype):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, description, price, stock, category, type) VALUES (?, ?, ?, ?, ?, ?)",
        (name, description, price, stock, category, ptype),
    )
    product_id = cur.lastrowid
    conn.commit()
    conn.close()
    return product_id


ALLOWED_PRODUCT_FIELDS = {"name", "description", "price", "stock", "category", "type"}


def update_product(product_id, **kwargs):
    conn = get_conn()
    cur = conn.cursor()
    for key, value in kwargs.items():
        if key not in ALLOWED_PRODUCT_FIELDS:
            continue
        cur.execute(f"UPDATE products SET {key} = ? WHERE id = ?", (value, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
    cur.execute("DELETE FROM product_delivery WHERE product_id = ?", (product_id,))
    conn.commit()
    conn.close()


def decrease_stock(product_id, qty):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE products SET stock = stock - ? WHERE id = ?",
        (qty, product_id),
    )
    conn.commit()
    conn.close()
