import logging
import sqlite3

from db.database import get_conn

logger = logging.getLogger(__name__)


def get_all_products():
    """Fetch all in-stock products. Returns empty list on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, price, stock, category, type FROM products WHERE stock > 0")
            return cur.fetchall()
    except sqlite3.Error as e:
        logger.error("Failed to fetch products: %s", e)
        return []


def get_product(product_id):
    """Fetch a single product by ID. Returns None on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, description, price, stock, category, type FROM products WHERE id = ?",
                (product_id,),
            )
            return cur.fetchone()
    except sqlite3.Error as e:
        logger.error("Failed to fetch product %d: %s", product_id, e)
        return None


def get_products_by_category(category):
    """Fetch in-stock products by category. Returns empty list on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name, price, stock, category, type FROM products WHERE category = ? AND stock > 0",
                (category,),
            )
            return cur.fetchall()
    except sqlite3.Error as e:
        logger.error("Failed to fetch products for category %r: %s", category, e)
        return []


def get_categories():
    """Fetch distinct categories with in-stock products. Returns empty list on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT category FROM products WHERE stock > 0")
            return [r[0] for r in cur.fetchall()]
    except sqlite3.Error as e:
        logger.error("Failed to fetch categories: %s", e)
        return []


def add_product(name, description, price, stock, category, ptype):
    """Add a new product. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO products (name, description, price, stock, category, type) VALUES (?, ?, ?, ?, ?, ?)",
                (name, description, price, stock, category, ptype),
            )
            product_id = cur.lastrowid
            conn.commit()
            return product_id
    except sqlite3.Error as e:
        logger.error("Failed to add product %r: %s", name, e)
        raise


def update_product(product_id, **kwargs):
    """Update product fields. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            for key, value in kwargs.items():
                cur.execute(f"UPDATE products SET {key} = ? WHERE id = ?", (value, product_id))
            conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to update product %d: %s", product_id, e)
        raise


def delete_product(product_id):
    """Delete a product and its delivery items. Raises on failure."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
            cur.execute("DELETE FROM product_delivery WHERE product_id = ?", (product_id,))
            conn.commit()
    except sqlite3.Error as e:
        logger.error("Failed to delete product %d: %s", product_id, e)
        raise


def decrease_stock(product_id, qty):
    """Decrease stock for a product. Raises on failure or insufficient stock."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
                (qty, product_id, qty),
            )
            if cur.rowcount == 0:
                raise ValueError(
                    f"Insufficient stock for product {product_id} (requested {qty})"
                )
            conn.commit()
    except sqlite3.Error as e:
        logger.error(
            "Failed to decrease stock for product %d by %d: %s",
            product_id, qty, e,
        )
        raise
