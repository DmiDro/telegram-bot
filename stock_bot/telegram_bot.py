import os
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from telegram.request import Request as TGRequest

# Переменные окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXY_URL = os.getenv("PROXY_URL")  # SOCKS5 proxy: socks5h://user:pass@host:port

# --- OpenAI логика ---
def get_openai_balance():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    try:
        response = requests.get("https://api.openai.com/dashboard/billing/credit_grants", headers=headers)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        return None

def format_balance_message():
    data = get_openai_balance()
    if data:
        return (
            "*OpenAI API — отчёт*\n\n"
            f"Остаток: ${data['total_available']:.2f} из ${data['total_granted']:.2f}\n"
            f"Потрачено: ${data['total_used']:.2f}\n\n"
            "_Всё под контролем._"
        )
    return "Ошибка при получении баланса OpenAI."

# --- Обработчики ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 Показать баланс", callback_data="check_balance")]]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=markup)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_balance_message(), parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(format_balance_message(), parse_mode="Markdown")

# --- Main запуск через polling и прокси ---
async def main():
    request = TGRequest(proxy_url=PROXY_URL) if PROXY_URL else None

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Запуск Telegram-бота с polling + proxy...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
