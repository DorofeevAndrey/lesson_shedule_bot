from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Кнопка 1", callback_data="button1")],
        [InlineKeyboardButton("Кнопка 2", callback_data="button2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет, настрой своё расписание.\n" "Для начала выбери что хочешь",
        reply_markup=reply_markup,
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "button1":
        await query.edit_message_text(text="Вы нажали Кнопку 1!")
    elif query.data == "button2":
        await query.edit_message_text(text="Вы нажали Кнопку 2!")


if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    application.run_polling()
