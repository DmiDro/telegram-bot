import os
import logging
import requests
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# Включаем логирование для Railway
logging.basicConfig(
    format='[%(asctime)s] %(levelname)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info("🚀 Бот запускается...")

# Переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- OpenAI логика ---
def get_openai_balance():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    try:
        response = requests.get("https://api.openai.com/dashboard/billing/credit_grants", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"OpenAI API вернул статус: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return None

def format_balance_message():
    data = get_openai_balance()
    if data:
        total = data.get("total_granted", 0)
        used = data.get("total_used", 0)
        available = data.get("total_available", 0)
        return (
            "*OpenAI API — отчёт*\n\n"
            f"Остаток: ${available:.2f} из ${total:.2f}\n"
            f"Потрачено: ${used:.2f}\n\n"
            "_Всё под контролем._"
        )
    return "❌ Ошибка при получении баланса OpenAI."

# --- Обработчики ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("➡️ Команда /start получена")
    keyboard = [[InlineKeyboardButton("📊 Показать баланс", callback_data="check_balance")]]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=markup)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("➡️ Команда /check получена")
    await update.message.reply_text(format_balance_message(), parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("🖱 Нажата кнопка 'Показать баланс'")
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(format_balance_message(), parse_mode="Markdown")

# --- Основной запуск ---
async def main():
    logger.info("⚙️ Инициализация Telegram Application...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CallbackQueryHandler(button_click))

    logger.info("✅ Бот запущен через polling")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
