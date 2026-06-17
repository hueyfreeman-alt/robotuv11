from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import WEBHOOK_HOST, WEBHOOK_PORT
from services.payment_service import create_invoice
from services.user_service import get_balance
from ui.keyboards import deposit_amounts, back_to_menu

router = Router()


class DepositState(StatesGroup):
    custom_amount = State()


@router.callback_query(lambda c: c.data == "deposit")
async def deposit_menu(callback: CallbackQuery):
    balance = get_balance(callback.from_user.id)
    await callback.message.edit_text(
        f"<b>Deposit</b>\n\nCurrent balance: {balance:.2f}$\n\nSelect amount:",
        parse_mode="HTML",
        reply_markup=deposit_amounts(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("dep_") and c.data != "dep_custom")
async def deposit_amount(callback: CallbackQuery):
    amount = float(callback.data.split("_")[1])
    await _process_deposit(callback, amount)


@router.callback_query(lambda c: c.data == "dep_custom")
async def deposit_custom(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DepositState.custom_amount)
    await callback.message.edit_text("Enter deposit amount (in $):")
    await callback.answer()


@router.message(DepositState.custom_amount)
async def deposit_custom_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount < 1:
            await message.answer("Minimum deposit is 1$.")
            return
    except (ValueError, TypeError):
        await message.answer("Invalid amount. Enter a number:")
        return

    await state.clear()
    callback_url = f"{WEBHOOK_HOST}:{WEBHOOK_PORT}/oxapay/callback" if WEBHOOK_HOST else ""
    track_id, payment_url = await create_invoice(message.from_user.id, amount, callback_url)

    if payment_url:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Pay Now", url=payment_url)],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="deposit")],
        ])
        await message.answer(
            f"<b>Payment Invoice</b>\n\nAmount: {amount}$\n\nClick below to pay:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    else:
        await message.answer(
            "Failed to create invoice. Please try again later.",
            reply_markup=back_to_menu(),
        )


async def _process_deposit(callback: CallbackQuery, amount: float):
    callback_url = f"{WEBHOOK_HOST}:{WEBHOOK_PORT}/oxapay/callback" if WEBHOOK_HOST else ""
    track_id, payment_url = await create_invoice(callback.from_user.id, amount, callback_url)

    if payment_url:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Pay Now", url=payment_url)],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="deposit")],
        ])
        await callback.message.edit_text(
            f"<b>Payment Invoice</b>\n\nAmount: {amount}$\n\nClick below to pay:",
            parse_mode="HTML",
            reply_markup=kb,
        )
    else:
        await callback.message.edit_text(
            "Failed to create invoice. Please try again later.",
            reply_markup=back_to_menu(),
        )
    await callback.answer()
