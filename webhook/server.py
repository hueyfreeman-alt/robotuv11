import logging

from aiohttp import web

from services.payment_service import (
    get_transaction_by_track,
    mark_transaction_paid,
    mark_transaction_credited,
    update_transaction_status,
    verify_callback_signature,
)
from services.user_service import add_balance

logger = logging.getLogger(__name__)

BOT_INSTANCE = None


def set_bot(bot):
    global BOT_INSTANCE
    BOT_INSTANCE = bot


async def oxapay_callback(request: web.Request):
    """Handle OxaPay payment callbacks."""
    raw_body = await request.read()
    received_hmac = request.headers.get("HMAC", "")

    # Verify signature
    if not verify_callback_signature(raw_body, received_hmac):
        logger.warning("Invalid HMAC signature on callback")
        return web.Response(text="invalid", status=403)

    try:
        data = await request.json()
    except Exception:
        return web.Response(text="bad request", status=400)

    track_id = data.get("trackId") or data.get("track_id", "")
    status = data.get("status", "")

    logger.info(f"OxaPay callback: track_id={track_id}, status={status}")

    if not track_id:
        return web.Response(text="ok")

    # Update transaction status
    update_transaction_status(track_id, status)

    if status == "paid":
        txn = get_transaction_by_track(track_id)
        if not txn:
            logger.warning(f"Transaction not found: {track_id}")
            return web.Response(text="ok")

        txn_id, telegram_id, _, amount, _, credited = txn

        # Prevent duplicate credits
        if credited:
            logger.info(f"Already credited: {track_id}")
            return web.Response(text="ok")

        # Credit user balance
        add_balance(telegram_id, amount)
        mark_transaction_paid(track_id)
        mark_transaction_credited(track_id)

        logger.info(f"Credited {amount}$ to user {telegram_id}")

        # Notify user
        if BOT_INSTANCE:
            try:
                await BOT_INSTANCE.send_message(
                    telegram_id,
                    f"<b>Deposit confirmed</b>\n\n"
                    f"Amount: {amount}$\n"
                    f"Your balance has been updated.",
                    parse_mode="HTML",
                )
            except Exception as e:
                logger.error(f"Failed to notify user {telegram_id}: {e}")

    return web.Response(text="ok")


def create_webhook_app():
    app = web.Application()
    app.router.add_post("/oxapay/callback", oxapay_callback)
    return app
