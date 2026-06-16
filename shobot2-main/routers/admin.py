from aiogram import Router
from aiogram.types import Message
from config import ADMIN_ID

router = Router()


@router.message(lambda m: m.text.startswith("/set"))
async def set_status(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        _, order_id, status = message.text.split("|")

        await message.answer(f"Order {order_id} → {status}")
    except:
        await message.answer("Format: /set|id|status")