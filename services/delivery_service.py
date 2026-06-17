async def deliver(bot, user_id, items):
    text = "📦 Delivery:\n\n"
    for name, price, qty in items:
        text += f"{name} x{qty}\n"
    await bot.send_message(user_id, text)
