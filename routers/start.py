from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from ui.keyboards import main_menu, back_to_menu
from services.settings_service import get_setting
from services.user_service import register_user

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    # Register user for broadcasts
    register_user(message.from_user.id, message.from_user.username or "")

    # Send promo media if configured
    promo_type = get_setting("promo_type")
    promo_file_id = get_setting("promo_file_id")

    if promo_type and promo_file_id:
        caption = get_setting("promo_caption", "")
        if promo_type == "gif":
            await message.answer_animation(promo_file_id, caption=caption or None)
        elif promo_type == "video":
            await message.answer_video(promo_file_id, caption=caption or None)
        elif promo_type == "photo":
            await message.answer_photo(promo_file_id, caption=caption or None)

    # Display main menu
    await message.answer(
        "Welcome! Choose an option below:",
        reply_markup=main_menu(),
    )


@router.callback_query(lambda c: c.data == "back_menu")
async def back_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Choose an option below:",
        reply_markup=main_menu(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "help")
async def help_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛍 <b>Shop</b> — Browse products\n"
        "🛒 <b>Cart</b> — View your cart\n\n"
        "Use the buttons to navigate.",
        parse_mode="HTML",
        reply_markup=back_to_menu(),
    )
    await callback.answer()
