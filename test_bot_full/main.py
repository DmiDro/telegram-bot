import os
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import commands, start, questions, unsubscribe
from handlers.results.results_main import router as results_router
from handlers.feedback import router as feedback_router
from schedule.sender import setup_scheduler  # Планировщик

print("🐍 main.py успешно запущен — Railway исполняет этот файл.")

# === Настройка логгера ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# === Получение токена из окружения (через Railway Variables) ===
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения Railway")

# === Инициализация бота и диспетчера ===
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# === Подключение роутеров ===
dp.include_routers(
    commands.router,
    start.router,
    questions.router,
    unsubscribe.router,
    results_router,
    feedback_router,
)

# === Главная точка входа ===
async def main():
    logging.info("⏳ Запуск бота...")

    try:
        setup_scheduler(bot)
        logging.info("🟢 Планировщик запущен.")
    except Exception as e:
        logging.error(f"❌ Ошибка запуска планировщика: {e}")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("✅ Webhook удалён. Бот готов к polling.")
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"🚨 Ошибка запуска polling: {e}")

if __name__ == "__main__":
    asyncio.run(main())
