import os
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Импорт всех маршрутизаторов
from handlers import commands, start, questions, unsubscribe
from handlers.results.results_main import router as results_router
from handlers.feedback import router as feedback_router
from schedule.sender import setup_scheduler

# === Загрузка переменных окружения ===
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ Переменная TELEGRAM_BOT_TOKEN не найдена в .env!")

# === Настройка логгера ===
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# === Инициализация бота и диспетчера ===
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# === Подключение всех маршрутизаторов ===
dp.include_routers(
    commands.router,
    start.router,
    questions.router,
    unsubscribe.router,
    results_router,
    feedback_router
)

# === Главная точка входа ===
async def main():
    logging.info("⏳ Запуск бота...")

    try:
        setup_scheduler(bot)
        logging.info("🟢 Планировщик инициализирован.")
    except Exception as e:
        logging.error(f"❌ Ошибка при запуске планировщика: {e}")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("✅ Webhook удалён. Бот готов к polling.")
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"🚨 Ошибка запуска polling: {e}")

if __name__ == "__main__":
    asyncio.run(main())
