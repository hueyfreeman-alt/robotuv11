from db.database import get_cursor


def get_all_products():
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, price, stock, category, type"
            " FROM products WHERE stock > 0",
        )
        return cur.fetchall()


def get_product(product_id):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, description, price, stock,"
            " category, type FROM products WHERE id = ?",
            (product_id,),
        )
        return cur.fetchone()


def get_products_by_category(category):
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, name, price, stock, category, type"
            " FROM products"
            " WHERE category = ? AND stock > 0",
            (category,),
        )
        return cur.fetchall()


def get_categories():
    with get_cursor() as cur:
        cur.execute(
            "SELECT DISTINCT category"
            " FROM products WHERE stock > 0",
        )
        return [r[0] for r in cur.fetchall()]


def add_product(name, description, price, stock, category, ptype):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO products"
            " (name, description, price, stock, category, type)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (name, description, price, stock, category, ptype),
        )
        return cur.lastrowid


def update_product(product_id, **kwargs):
    with get_cursor() as cur:
        for key, value in kwargs.items():
            cur.execute(
                f"UPDATE products SET {key} = ? WHERE id = ?",
                (value, product_id),
            )


def delete_product(product_id):
    with get_cursor() as cur:
        cur.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,),
        )
        cur.execute(
            "DELETE FROM product_delivery WHERE product_id = ?",
            (product_id,),
        )


def decrease_stock(product_id, qty):
    with get_cursor() as cur:
        cur.execute(
            "UPDATE products SET stock = stock - ?"
            " WHERE id = ?",
            (qty, product_id),
        )
