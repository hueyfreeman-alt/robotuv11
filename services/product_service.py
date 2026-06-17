from db.database import get_conn


def get_products_by_vendor(vendor_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, vendor_id, city_id, name, description, price, stock, category, type, allow_preorder FROM products WHERE vendor_id = ?",
        (vendor_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_products_by_city(city_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, vendor_id, city_id, name, description, price, stock, category, type, allow_preorder FROM products WHERE city_id = ? AND (stock > 0 OR allow_preorder = 1)",
        (city_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_available_products_by_vendor(vendor_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, vendor_id, city_id, name, description, price, stock, category, type, allow_preorder FROM products WHERE vendor_id = ? AND (stock > 0 OR allow_preorder = 1)",
        (vendor_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_product(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, vendor_id, city_id, name, description, price, stock, category, type, allow_preorder FROM products WHERE id = ?",
        (product_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def add_product(vendor_id, city_id, name, description, price, stock, category, ptype, allow_preorder=0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO products (vendor_id, city_id, name, description, price, stock, category, type, allow_preorder)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (vendor_id, city_id, name, description, price, stock, category, ptype, allow_preorder),
    )
    product_id = cur.lastrowid
    conn.commit()
    conn.close()
    return product_id


def update_product(product_id, **kwargs):
    conn = get_conn()
    cur = conn.cursor()
    for key, value in kwargs.items():
        cur.execute(f"UPDATE products SET {key} = ? WHERE id = ?", (value, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM product_delivery WHERE product_id = ?", (product_id,))
    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
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


def get_product_owner(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT vendor_id FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
