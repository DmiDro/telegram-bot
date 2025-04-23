from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from telegram.ext import (
    ApplicationBuilder, Application, CommandHandler,
    CallbackQueryHandler, ContextTypes
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import os, requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

telegram_app: Application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# Telegram handlers
def get_openai_balance():
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    response = requests.get("https://api.openai.com/dashboard/billing/credit_grants", headers=headers)
    return response.json() if response.status_code == 200 else None

def format_balance_message():
    data = get_openai_balance()
    if data:
        return (
            "*OpenAI API — отчёт*\n\n"
            f"Остаток: ${data['total_available']:.2f} из ${data['total_granted']:.2f}\n"
            f"Потрачено: ${data['total_used']:.2f}\n\n"
            "_Всё под контролем._"
        )
    return "Ошибка при получении баланса."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("📊 Показать баланс", callback_data="check_balance")]])
    await update.message.reply_text("Выберите действие:", reply_markup=markup)

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(format_balance_message(), parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(format_balance_message(), parse_mode="Markdown")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("check", check))
telegram_app.add_handler(CallbackQueryHandler(button_click))

# Lifespan init
@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
