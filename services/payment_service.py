import hashlib
import hmac
import time

import aiohttp

from db.database import get_conn
from config import OXAPAY_MERCHANT_KEY

OXAPAY_API_URL = "https://api.oxapay.com/v1"


async def create_invoice(telegram_id, amount, callback_url):
    """Create an OxaPay invoice and return (track_id, payment_url)."""
    payload = {
        "amount": amount,
        "callback_url": callback_url,
        "order_id": f"dep_{telegram_id}_{int(time.time())}",
        "description": f"Deposit for user {telegram_id}",
        "sandbox": False,
    }
    headers = {
        "Authorization": f"Bearer {OXAPAY_MERCHANT_KEY}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{OXAPAY_API_URL}/payment/invoice",
            json=payload,
            headers=headers,
        ) as resp:
            data = await resp.json()

    if data.get("status") == 200 and data.get("data"):
        track_id = data["data"]["track_id"]
        payment_url = data["data"]["payment_url"]
        # Store transaction
        save_transaction(telegram_id, track_id, amount)
        return track_id, payment_url

    return None, None


def save_transaction(telegram_id, track_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (telegram_id, track_id, amount) VALUES (?, ?, ?)",
        (telegram_id, track_id, amount),
    )
    conn.commit()
    conn.close()


def get_transaction_by_track(track_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, telegram_id, track_id, amount, status, credited FROM transactions WHERE track_id = ?",
        (track_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def mark_transaction_paid(track_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE transactions SET status = 'paid', paid_at = CURRENT_TIMESTAMP WHERE track_id = ?",
        (track_id,),
    )
    conn.commit()
    conn.close()


def mark_transaction_credited(track_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE transactions SET credited = 1 WHERE track_id = ?",
        (track_id,),
    )
    conn.commit()
    conn.close()


def update_transaction_status(track_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE transactions SET status = ? WHERE track_id = ?",
        (status, track_id),
    )
    conn.commit()
    conn.close()


def verify_callback_signature(raw_body: bytes, received_hmac: str) -> bool:
    """Verify OxaPay HMAC-SHA512 callback signature."""
    expected = hmac.HMAC(
        OXAPAY_MERCHANT_KEY.encode(),
        raw_body,
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(expected, received_hmac)
