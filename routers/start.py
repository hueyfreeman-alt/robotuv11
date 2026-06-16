from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from ui.keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🏪 Welcome to Shop Bot V11",
        reply_markup=main_menu()
    )