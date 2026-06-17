import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from db.database import init_db

from routers.start import router as start_router
from routers.shop import router as shop_router
from routers.cart import router as cart_router
from routers.checkout import router as checkout_router
from routers.admin import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start_router)
dp.include_router(shop_router)
dp.include_router(cart_router)
dp.include_router(checkout_router)
dp.include_router(admin_router)


async def main():
    try:
        init_db()
    except Exception as e:
        logger.critical("Failed to initialize database, shutting down: %s", e)
        sys.exit(1)

    logger.info("Bot starting...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical("Bot crashed: %s", e)
        sys.exit(1)



if __name__ == "__main__":
    asyncio.run(main())
