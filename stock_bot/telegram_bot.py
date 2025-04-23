import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # <- твой Railway-домен https://your-app.up.railway.app

def get_openai_balance():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    response = requests.get("https://api.openai.com/dashboard/billing/credit_grants", headers=headers)
    return response.json() if response.status_code == 200 else None

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
    else:
        return "Ошибка при получении баланса OpenAI."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 Показать баланс", callback_data="check_balance")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = format_balance_message()
    await update.message.reply_text(msg, parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_balance":
        msg = format_balance_message()
        await query.edit_message_text(msg, parse_mode="Markdown")

# Webhook-бот без FastAPI
if __name__ == "__main__":
    from telegram.ext import Application

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CallbackQueryHandler(button_click))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )
