from aiogram import Router
from aiogram.types import CallbackQuery

from ui.keyboards import back_to_menu
from services.settings_service import get_setting

router = Router()

DEFAULT_GUIDE = (
    "<b>How to use this bot:</b>\n\n"
    "1. <b>Shop Now</b> — Browse products by city and vendor\n"
    "2. <b>Deposit</b> — Add funds via crypto (OxaPay)\n"
    "3. <b>Profile</b> — View balance, orders, tickets\n"
    "4. <b>Courier</b> — Physical delivery (preorder)\n\n"
    "After purchase, digital items are delivered instantly.\n"
    "You can leave reviews and open tickets within 6 hours."
)

DEFAULT_RULES = (
    "<b>Rules:</b>\n\n"
    "1. No chargebacks or disputes outside the ticket system.\n"
    "2. Tickets must be opened within 6 hours of purchase.\n"
    "3. Vendors must deliver within the agreed timeframe.\n"
    "4. Abuse of the system will result in a ban.\n"
    "5. All sales are final once delivery is confirmed."
)


@router.callback_query(lambda c: c.data == "help_guide")
async def guide(callback: CallbackQuery):
    text = get_setting("guide_text") or DEFAULT_GUIDE
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_to_menu())
    await callback.answer()


@router.callback_query(lambda c: c.data == "help_rules")
async def rules(callback: CallbackQuery):
    text = get_setting("rules_text") or DEFAULT_RULES
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_to_menu())
    await callback.answer()
