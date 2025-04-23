import os
import requests
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, ApplicationBuilder, ContextTypes,
    CommandHandler, CallbackQueryHandler,
)
from telegram.ext.webhookhandler import WebhookRequestHandler

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # пример: https://yourapp.up.railway.app

app = FastAPI()

# Telegram Application (async bot)
telegram_app: Application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# --- Функции бота ---
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

# --- Обработчики ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📊 Показать баланс", callback_data="check_balance")]]
    await update.message.reply_text("Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard))

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = format_balance_message()
    await update.message.reply_text(msg, parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg = format_balance_message()
    await query.edit_message_text(msg, parse_mode="Markdown")

# --- Подключаем обработчики ---
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("check", check))
telegram_app.add_handler(CallbackQueryHandler(button_click))

# --- Инициализация вебхука при запуске ---
@app.on_event("startup")
async def on_startup():
    await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

# --- Эндпоинт для Telegram Webhook ---
@app.post("/webhook")
async def telegram_webhook(request: Request):
    update_data = await request.json()
    update = Update.de_json(update_data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"
