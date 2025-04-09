# 📄 test_bot_full/main.py

import os
import logging
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

# 👇 Импорт всех маршрутизаторов
from test_bot_full.handlers import commands, start, questions, unsubscribe
from test_bot_full.handlers.results.results_main import router as results_router
from test_bot_full.handlers.feedback import router as feedback_router
from test_bot_full.schedule.sender import setup_scheduler

# === Загрузка переменных окружения из .env ===
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ Переменная TELEGRAM_BOT_TOKEN не найдена в .env!")

# === Инициализация бота и диспетчера ===
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# === Подключение всех обработчиков ===
dp.include_routers(
    commands.router,
    start.router,
    questions.router,
    unsubscribe.router,
    results_router,
    feedback_router
)

# === Главная точка запуска ===
async def on_start():
    logging.basicConfig(level=logging.INFO)
    logging.info("⏳ Запуск бота...")
    setup_scheduler(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("✅ Бот запущен!")
    await dp.start_polling(bot)

# === Для gunicorn ===
if __name__ == "__main__":
    # Для gunicorn необходимо использовать эту переменную
    app = dp

    # Если вам нужно использовать asyncio для запуска бота:
    # asyncio.run(on_start())
