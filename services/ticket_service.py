import datetime

from db.database import get_conn

TICKET_WINDOW_HOURS = 6


def can_create_ticket(order_id):
    """Check if ticket can be created (within 6hr of order)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT created_at FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    try:
        order_time = datetime.datetime.fromisoformat(row[0])
    except (ValueError, TypeError):
        order_time = datetime.datetime.now()
    elapsed = datetime.datetime.now() - order_time
    return elapsed.total_seconds() < TICKET_WINDOW_HOURS * 3600


def create_ticket(order_id, customer_id, vendor_id, subject):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tickets (order_id, customer_id, vendor_id, subject) VALUES (?, ?, ?, ?)",
        (order_id, customer_id, vendor_id, subject),
    )
    ticket_id = cur.lastrowid
    conn.commit()
    conn.close()
    return ticket_id


def add_ticket_message(ticket_id, sender_id, message):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ticket_messages (ticket_id, sender_id, message) VALUES (?, ?, ?)",
        (ticket_id, sender_id, message),
    )
    conn.commit()
    conn.close()


def get_ticket(ticket_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, order_id, customer_id, vendor_id, subject, status, created_at FROM tickets WHERE id = ?",
        (ticket_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_ticket_messages(ticket_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, sender_id, message, created_at FROM ticket_messages WHERE ticket_id = ? ORDER BY created_at",
        (ticket_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_customer_tickets(customer_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, order_id, subject, status, created_at FROM tickets WHERE customer_id = ? ORDER BY created_at DESC",
        (customer_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_vendor_tickets(vendor_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, order_id, customer_id, subject, status, created_at FROM tickets WHERE vendor_id = ? ORDER BY created_at DESC",
        (vendor_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def close_ticket(ticket_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET status = 'closed' WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()


def respond_ticket(ticket_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET status = 'responded' WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
