import os
import logging
import requests
import asyncio
import nest_asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# --- Логирование ---
logging.basicConfig(
    format='[%(asctime)s] %(levelname)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info("\U0001F680 Бот запускается...")

# --- Переменные окружения ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Прямой запрос в OpenAI ---
def get_openai_balance():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    try:
        response = requests.get(
            "https://api.openai.com/dashboard/billing/credit_grants",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_granted", 0)
            used = data.get("total_used", 0)
            available = data.get("total_available", 0)
            return f"Остаток: ${available:.2f} из ${total:.2f}\nПотрачено: ${used:.2f}"
        else:
            return f"\u274C Ошибка от OpenAI: {response.status_code}"
    except Exception as e:
        return f"\u274C Ошибка при запросе к OpenAI: {e}"

# --- Формирование ответа ---
def format_balance_message():
    content = get_openai_balance()
    return f"*Отчёт по OpenAI:*

{content}"

# --- Обработчики ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("\u27A1\uFE0F Команда /start получена")
    keyboard = [[InlineKeyboardButton("\ud83d\udcca Показать баланс", callback_data="check_balance")]]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=markup)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("\u27A1\uFE0F Команда /check получена")
    await update.message.reply_text(format_balance_message(), parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("\ud83d\udd39 Нажата кнопка 'Показать баланс'")
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(format_balance_message(), parse_mode="Markdown")

# --- Основной запуск ---
async def main():
    logger.info("\u2699\ufe0f Инициализация Telegram Application...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CallbackQueryHandler(button_click))

    logger.info("\u2705 Бот запущен через polling")
    await app.run_polling()

if __name__ == "__main__":
    logger.info("\U0001F501 Запуск через nest_asyncio loop...")
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
