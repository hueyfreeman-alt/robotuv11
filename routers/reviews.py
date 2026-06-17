from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.review_service import (
    add_review, get_product_reviews, has_reviewed_order, get_product_rating,
)
from services.order_service import get_order, get_order_items, mark_order_reviewed
from ui.keyboards import stars_keyboard, back_to_menu

router = Router()


class ReviewState(StatesGroup):
    text = State()


@router.callback_query(lambda c: c.data.startswith("review_"))
async def review_order(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[1])
    order = get_order(order_id)
    if not order or order[1] != callback.from_user.id:
        await callback.answer("Order not found")
        return

    if order[6]:  # reviewed
        await callback.answer("Already reviewed")
        return

    if has_reviewed_order(order_id, callback.from_user.id):
        await callback.answer("Already reviewed")
        return

    items = get_order_items(order_id)
    if not items:
        await callback.answer("No items to review")
        return

    product_id = items[0][0]
    await callback.message.edit_text(
        "<b>Rate your purchase:</b>",
        parse_mode="HTML",
        reply_markup=stars_keyboard(order_id, product_id),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("star_"))
async def set_stars(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    stars = int(parts[1])
    order_id = int(parts[2])
    product_id = int(parts[3])

    await state.update_data(stars=stars, order_id=order_id, product_id=product_id)
    await state.set_state(ReviewState.text)
    await callback.message.edit_text(
        f"Rating: {'⭐' * stars}\n\nNow enter your review text (or send /skip):"
    )
    await callback.answer()


@router.message(ReviewState.text)
async def review_text(message: Message, state: FSMContext):
    data = await state.get_data()
    stars = data["stars"]
    order_id = data["order_id"]
    product_id = data["product_id"]

    text = "" if message.text == "/skip" else (message.text or "")

    order = get_order(order_id)
    if not order:
        await state.clear()
        await message.answer("Order not found.", reply_markup=back_to_menu())
        return

    vendor_id = order[2]

    add_review(order_id, product_id, vendor_id, message.from_user.id, stars, text)
    mark_order_reviewed(order_id)
    await state.clear()

    await message.answer(
        f"Thank you! Your {stars}-star review has been submitted.",
        reply_markup=back_to_menu(),
    )


@router.callback_query(lambda c: c.data.startswith("rev_"))
async def view_product_reviews(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    reviews = get_product_reviews(product_id)
    avg, count = get_product_rating(product_id)

    if not reviews:
        await callback.message.edit_text("No reviews yet.", reply_markup=back_to_menu())
        await callback.answer()
        return

    lines = [f"<b>Reviews</b> ({avg}/5 from {count} reviews)\n"]
    for r_id, stars, text, created, username in reviews:
        line = f"{'⭐' * stars} by @{username or 'anon'}"
        if text:
            line += f"\n  <i>{text}</i>"
        lines.append(line)

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=back_to_menu(),
    )
    await callback.answer()
