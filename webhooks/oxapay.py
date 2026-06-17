import hashlib
import hmac
import json
import logging

from aiohttp import web

from config import ADMIN_ID, OXAPAY_MERCHANT_API_KEY
from services.delivery_service import deliver_by_product_ids
from services.order_service import get_order, get_order_items, update_order_status
from services.payment_service import (
    get_payment_by_track_id,
    update_payment_status_by_track_id,
)
from services.product_service import decrease_stock

logger = logging.getLogger(__name__)


def setup_oxapay_routes(app):
    app.router.add_post("/webhooks/oxapay", handle_oxapay_webhook)
    app.router.add_get("/health", health_check)


async def health_check(request):
    return web.Response(text="ok")


def verify_hmac(body: bytes, hmac_header: str | None) -> bool:
    if not hmac_header:
        return False
    calculated = hmac.new(
        OXAPAY_MERCHANT_API_KEY.encode(),
        body,
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(calculated, hmac_header)


async def handle_oxapay_webhook(request):
    body = await request.read()
    if not verify_hmac(body, request.headers.get("HMAC")):
        return web.Response(status=400, text="Invalid HMAC signature")

    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

    if payload.get("type") != "invoice":
        return web.Response(text="ok")

    track_id = str(payload.get("track_id") or payload.get("trackId") or "")
    raw_status = str(payload.get("status") or "")
    status = raw_status.lower()
    if not track_id or not status:
        return web.Response(status=400, text="Missing track_id/status")

    update_payment_status_by_track_id(track_id, status, raw_status)

    if status == "paid":
        try:
            await fulfill_paid_order(request.app["bot"], track_id)
        except Exception:
            logger.exception("Failed to fulfill paid OxaPay order for track_id=%s", track_id)
            payment = get_payment_by_track_id(track_id)
            order_id = payment[1] if payment else "unknown"
            await notify_admin_fulfillment_failed(request.app["bot"], order_id, track_id)
            return web.Response(status=500, text="Fulfillment failed")

    return web.Response(text="ok")


async def fulfill_paid_order(bot, track_id: str):
    payment = get_payment_by_track_id(track_id)
    if not payment:
        logger.warning("Received paid OxaPay webhook for unknown track_id=%s", track_id)
        return

    _, order_id, _, _, _, _, _, _ = payment
    order = get_order(order_id)
    if not order:
        logger.warning("Received paid OxaPay webhook for missing order_id=%s", order_id)
        return

    _, telegram_id, total, order_status, _ = order
    if order_status in {"fulfilling", "completed"}:
        return

    update_order_status(order_id, "fulfilling")

    items = get_order_items(order_id)
    product_ids = []
    for product_id, quantity in items:
        decrease_stock(product_id, quantity)
        product_ids.append(product_id)

    await deliver_by_product_ids(bot, telegram_id, product_ids)
    await bot.send_message(
        telegram_id,
        f"<b>Order #{order_id} paid</b>\n"
        f"Total: {total}$\n\n"
        "Your digital items have been delivered above.",
        parse_mode="HTML",
    )
    update_order_status(order_id, "completed")
    update_payment_status_by_track_id(track_id, "paid", "Paid")


async def notify_admin_fulfillment_failed(bot, order_id, track_id):
    try:
        await bot.send_message(
            ADMIN_ID,
            f"OxaPay payment was confirmed but fulfillment failed.\n"
            f"Order: #{order_id}\n"
            f"Track ID: {track_id}",
        )
    except Exception:
        logger.exception("Failed to notify admin about OxaPay fulfillment failure")
