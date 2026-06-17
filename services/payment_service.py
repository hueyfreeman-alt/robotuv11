import asyncio

import aiohttp

from config import (
    OXAPAY_CALLBACK_URL,
    OXAPAY_CURRENCY,
    OXAPAY_MERCHANT_API_KEY,
    OXAPAY_RETURN_URL,
    OXAPAY_SANDBOX,
)
from db.database import get_conn

OXAPAY_INVOICE_URL = "https://api.oxapay.com/v1/payment/invoice"


class OxaPayError(RuntimeError):
    pass


def create_payment(
    order_id,
    amount,
    provider="oxapay",
    status="pending",
    track_id=None,
    payment_url="",
    raw_status="",
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO payments
            (order_id, amount, provider, status, track_id, payment_url, raw_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (order_id, amount, provider, status, track_id, payment_url, raw_status),
    )
    payment_id = cur.lastrowid
    conn.commit()
    conn.close()
    return payment_id


async def create_oxapay_invoice(order_id, amount):
    payload = {
        "amount": float(amount),
        "callback_url": OXAPAY_CALLBACK_URL,
        "order_id": str(order_id),
        "description": f"Telegram shop order #{order_id}",
        "sandbox": OXAPAY_SANDBOX,
    }
    if OXAPAY_CURRENCY:
        payload["currency"] = OXAPAY_CURRENCY
    if OXAPAY_RETURN_URL:
        payload["return_url"] = OXAPAY_RETURN_URL

    timeout = aiohttp.ClientTimeout(total=20)
    headers = {
        "Content-Type": "application/json",
        "merchant_api_key": OXAPAY_MERCHANT_API_KEY,
    }

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(OXAPAY_INVOICE_URL, json=payload, headers=headers) as response:
                response_data = await response.json(content_type=None)
                status_code = response.status
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as exc:
        raise OxaPayError(f"OxaPay invoice request failed: {exc}") from exc

    if not isinstance(response_data, dict):
        raise OxaPayError("OxaPay invoice response was not a JSON object")

    if status_code != 200 or response_data.get("status") != 200 or response_data.get("error"):
        message = response_data.get("message") or response_data.get("error") or response_data
        raise OxaPayError(f"OxaPay invoice creation failed: {message}")

    invoice = response_data.get("data") or {}
    track_id = invoice.get("track_id")
    payment_url = invoice.get("payment_url")
    if not track_id or not payment_url:
        raise OxaPayError("OxaPay response did not include track_id/payment_url")

    create_payment(
        order_id=order_id,
        amount=amount,
        track_id=track_id,
        payment_url=payment_url,
        status="pending",
        raw_status="invoice_created",
    )
    return invoice


def get_payment_by_track_id(track_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, order_id, amount, provider, status, track_id, payment_url, raw_status
        FROM payments
        WHERE track_id = ?
        """,
        (track_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def update_payment_status_by_track_id(track_id, status, raw_status=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE payments
        SET status = ?, raw_status = COALESCE(?, raw_status)
        WHERE track_id = ?
        """,
        (status, raw_status, track_id),
    )
    conn.commit()
    conn.close()
