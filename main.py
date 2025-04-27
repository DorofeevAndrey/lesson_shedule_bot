from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TOKEN
from handlers import start, button
from database import create_tables


def main():
    create_tables()
    # Создаем приложение с токеном
    application = Application.builder().token(TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
