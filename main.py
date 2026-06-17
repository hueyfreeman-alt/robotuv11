import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN, WEBHOOK_HOST, WEBHOOK_PORT
from db.database import init_db
from webhook.server import create_webhook_app, set_bot

from routers.start import router as start_router
from routers.shop import router as shop_router
from routers.cart import router as cart_router
from routers.checkout import router as checkout_router
from routers.admin import router as admin_router
from routers.profile import router as profile_router
from routers.deposit import router as deposit_router
from routers.vendor import router as vendor_router
from routers.reviews import router as reviews_router
from routers.tickets import router as tickets_router
from routers.courier import router as courier_router
from routers.help import router as help_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start_router)
dp.include_router(shop_router)
dp.include_router(cart_router)
dp.include_router(checkout_router)
dp.include_router(profile_router)
dp.include_router(deposit_router)
dp.include_router(vendor_router)
dp.include_router(reviews_router)
dp.include_router(tickets_router)
dp.include_router(courier_router)
dp.include_router(help_router)
dp.include_router(admin_router)


async def start_webhook_server():
    """Start aiohttp server for OxaPay callbacks."""
    if not WEBHOOK_HOST:
        return
    app = create_webhook_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
    await site.start()
    logging.info(f"Webhook server started on port {WEBHOOK_PORT}")


async def main():
    init_db()
    set_bot(bot)

    if WEBHOOK_HOST:
        await start_webhook_server()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
