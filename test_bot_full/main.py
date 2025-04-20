import os
import logging
import asyncio
import httpx

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import commands, start, questions, unsubscribe
from handlers.results.results_main import router as results_router
from handlers.feedback import router as feedback_router
from schedule.sender import setup_scheduler  # Планировщик

# === Настройка логгера ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

print("🐍 main.py успешно запущен — Railway исполняет этот файл.")

# === Получение токенов и прокси ===
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROXY = os.getenv("OPENAI_PROXY", "").strip()

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в переменных окружения Railway")

# === Проверка прокси соединения (асинхронная) ===
async def test_proxy():
    if not OPENAI_PROXY:
        logging.warning("⚠️ OPENAI_PROXY не задан, проверка пропущена")
        return
    if OPENAI_PROXY.startswith("socks5h://"):
        OPENAI_PROXY_FIXED = "socks5://" + OPENAI_PROXY[len("socks5h://"):]
    else:
        OPENAI_PROXY_FIXED = OPENAI_PROXY
    try:
        async with httpx.AsyncClient(proxies={"all://": OPENAI_PROXY_FIXED}, timeout=10) as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
            )
            logging.info(f"✅ Прокси работает, статус: {response.status_code}")
    except Exception as e:
        logging.error(f"❌ Прокси не работает: {e}")

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

    await test_proxy()  # Проверка OpenAI через прокси

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
