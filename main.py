import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from config import TOKEN, WEBHOOK_HOST, WEBHOOK_PORT
from db.database import init_db

from routers.start import router as start_router
from routers.shop import router as shop_router
from routers.cart import router as cart_router
from routers.checkout import router as checkout_router
from routers.admin import router as admin_router
from webhooks.oxapay import setup_oxapay_routes

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start_router)
dp.include_router(shop_router)
dp.include_router(cart_router)
dp.include_router(checkout_router)
dp.include_router(admin_router)


async def start_webhook_server():
    app = web.Application()
    app["bot"] = bot
    setup_oxapay_routes(app)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBHOOK_HOST, WEBHOOK_PORT)
    await site.start()
    return runner


async def main():
    init_db()
    webhook_runner = await start_webhook_server()
    try:
        await dp.start_polling(bot)
    finally:
        await webhook_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
