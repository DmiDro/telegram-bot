import os
import asyncio
import logging
import httpx
from openai import AsyncOpenAI

# === Настройка логгера ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# === Переменные окружения ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROXY = os.getenv("OPENAI_PROXY", "").strip()

# === Приведение схемы прокси к поддерживаемой формe (если указана socks5h)
if OPENAI_PROXY.startswith("socks5h://"):
    OPENAI_PROXY = "socks5://" + OPENAI_PROXY[len("socks5h://"):]

logging.info(f"🔌 OPENAI_PROXY: {repr(OPENAI_PROXY)}")

# === Тестовая функция ===
async def check_openai_via_proxy():
    try:
        http_client = httpx.AsyncClient(
            proxies={"all://": OPENAI_PROXY},
            timeout=30.0
        )

        client = AsyncOpenAI(
            api_key=OPENAI_API_KEY,
            http_client=http_client
        )

        prompt = "Напиши мне короткий ответ"

        logging.info("📤 Отправляем промт в OpenAI...")
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content.strip()
        logging.info(f"✅ Ответ от GPT:\n{content}")

    except Exception as e:
        logging.error(f"❌ Ошибка при подключении через прокси: {e}")

# === Запуск ===
if __name__ == "__main__":
    asyncio.run(check_openai_via_proxy())
