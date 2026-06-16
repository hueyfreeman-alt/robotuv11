import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from db.database import init_db

from routers.start import router as start_router
from routers.shop import router as shop_router
from routers.cart import router as cart_router
from routers.checkout import router as checkout_router
from routers.admin import router as admin_router

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(shop_router)
dp.include_router(cart_router)
dp.include_router(checkout_router)
dp.include_router(admin_router)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
