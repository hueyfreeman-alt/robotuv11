from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from services.product_service import get_all_products
from services.cart_service import add_to_cart

router = Router()


@router.callback_query(lambda c: c.data == "shop")
async def shop(callback: CallbackQuery):
    products = get_all_products()

    if not products:
        await callback.message.answer("❌ No products")
        return

    for p in products:
        pid, name, price, stock, category, ptype = p

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add", callback_data=f"add_{pid}")]
        ])

        await callback.message.answer(
            f"📦 {name}\n💰 {price}$\n📦 Stock: {stock}",
            reply_markup=kb
        )

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("add_"))
async def add(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])

    add_to_cart(callback.from_user.id, product_id, 1)

    await callback.answer("Added ✅")