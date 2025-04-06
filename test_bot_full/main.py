import os
import logging
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from test_bot_full.handlers import commands, start, questions, unsubscribe
from test_bot_full.handlers.results.results_main import router as results_router
from test_bot_full.handlers.feedback import router as feedback_router
from test_bot_full.schedule.sender import setup_scheduler

# === Загрузка .env ===
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# === Настройка бота ===
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# === Подключение роутеров ===
dp.include_routers(
    commands.router,     # 🟢 Теперь dp уже определён
    start.router,
    questions.router,
    unsubscribe.router,
    results_router,
    feedback_router
)

# === Запуск ===
async def main():
    logging.basicConfig(level=logging.INFO)
    setup_scheduler(bot)
    logging.info("✅ Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
