from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.ticket_service import (
    can_create_ticket, create_ticket, add_ticket_message,
    get_ticket, get_ticket_messages, get_customer_tickets, close_ticket,
)
from services.order_service import get_order
from ui.keyboards import back_to_menu

router = Router()


class TicketState(StatesGroup):
    subject = State()
    message = State()
    reply = State()


@router.callback_query(lambda c: c.data.startswith("ticket_"))
async def open_ticket(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[1])
    order = get_order(order_id)
    if not order or order[1] != callback.from_user.id:
        await callback.answer("Order not found")
        return

    if not can_create_ticket(order_id):
        await callback.message.edit_text(
            "Ticket window expired (6 hours after purchase).",
            reply_markup=back_to_menu(),
        )
        await callback.answer()
        return

    await state.update_data(order_id=order_id, vendor_id=order[2])
    await state.set_state(TicketState.subject)
    await callback.message.edit_text("Enter the subject of your ticket:")
    await callback.answer()


@router.message(TicketState.subject)
async def ticket_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(TicketState.message)
    await message.answer("Describe your issue:")


@router.message(TicketState.message)
async def ticket_message(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data["order_id"]
    vendor_id = data["vendor_id"]
    subject = data["subject"]

    ticket_id = create_ticket(order_id, message.from_user.id, vendor_id, subject)
    add_ticket_message(ticket_id, message.from_user.id, message.text)

    await state.clear()
    await message.answer(
        f"Ticket #{ticket_id} created. The vendor will respond soon.",
        reply_markup=back_to_menu(),
    )


@router.callback_query(lambda c: c.data == "my_tickets")
async def my_tickets(callback: CallbackQuery):
    tickets = get_customer_tickets(callback.from_user.id)
    if not tickets:
        await callback.message.edit_text("No tickets.", reply_markup=back_to_menu())
        await callback.answer()
        return

    buttons = []
    for t_id, order_id, subject, status, created in tickets:
        buttons.append([InlineKeyboardButton(
            text=f"#{t_id} [{status}] {subject[:20]}",
            callback_data=f"viewticket_{t_id}",
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="profile")])

    await callback.message.edit_text(
        "<b>Your Tickets</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("viewticket_"))
async def view_ticket(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[1])
    ticket = get_ticket(ticket_id)
    if not ticket or ticket[2] != callback.from_user.id:
        await callback.answer("Ticket not found")
        return

    messages = get_ticket_messages(ticket_id)
    lines = [f"<b>Ticket #{ticket_id}: {ticket[4]}</b>\nStatus: {ticket[5]}\n"]
    for _, sender_id, msg, created in messages:
        who = "You" if sender_id == callback.from_user.id else "Vendor"
        lines.append(f"<b>{who}</b> ({created[:16]})\n{msg}\n")

    buttons = []
    if ticket[5] != "closed":
        buttons.append([InlineKeyboardButton(text="Reply", callback_data=f"treply_{ticket_id}")])
        buttons.append([InlineKeyboardButton(text="Close", callback_data=f"tclose_{ticket_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="my_tickets")])

    await callback.message.edit_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("treply_"))
async def ticket_reply(callback: CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.split("_")[1])
    await state.update_data(reply_ticket_id=ticket_id)
    await state.set_state(TicketState.reply)
    await callback.message.edit_text("Enter your reply:")
    await callback.answer()


@router.message(TicketState.reply)
async def ticket_reply_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket_id = data["reply_ticket_id"]
    add_ticket_message(ticket_id, message.from_user.id, message.text)
    await state.clear()
    await message.answer("Reply sent.", reply_markup=back_to_menu())


@router.callback_query(lambda c: c.data.startswith("tclose_"))
async def ticket_close(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[1])
    close_ticket(ticket_id)
    await callback.message.edit_text("Ticket closed.", reply_markup=back_to_menu())
    await callback.answer()
