import os
import requests
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    Dispatcher,
    CallbackContext,
    CommandHandler,
    CallbackQueryHandler,
)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

app = FastAPI()
scheduler = BackgroundScheduler()
bot = Bot(token=TELEGRAM_BOT_TOKEN)

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

def weekly_report():
    msg = format_balance_message()
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode="Markdown")

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📊 Показать баланс", callback_data="check_balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Выберите действие:", reply_markup=reply_markup)

def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == "check_balance":
        msg = format_balance_message()
        query.edit_message_text(text=msg, parse_mode="Markdown")

@app.on_event("startup")
def start_all():
    scheduler.add_job(weekly_report, "cron", day_of_week="fri", hour=9, minute=0)
    scheduler.start()

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_click))

    updater.start_polling()
