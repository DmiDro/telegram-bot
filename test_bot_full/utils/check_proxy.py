import os
import asyncio
import logging
import httpx
from openai import AsyncOpenAI

# Настройка логгера
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# Получаем переменные окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROXY = os.getenv("OPENAI_PROXY", "").strip()

# Обработка формата прокси
if OPENAI_PROXY.startswith("socks5h://"):
    OPENAI_PROXY = "socks5://" + OPENAI_PROXY[len("socks5h://"):]

logging.info(f"🔌 OPENAI_PROXY: {repr(OPENAI_PROXY)}")

# Основная проверка
async def main():
    logging.info("📤 Отправляем запрос к OpenAI через прокси...")

    # Настраиваем httpx-клиент с прокси
    http_client = httpx.AsyncClient(
        proxies={"all://": OPENAI_PROXY} if OPENAI_PROXY else None,
        timeout=30.0
    )

    # Создаём клиента OpenAI
    client = AsyncOpenAI(
        api_key=OPENAI_API_KEY,
        http_client=http_client
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Напиши мне короткий ответ"}]
        )
        answer = response.choices[0].message.content.strip()
        logging.info(f"✅ Ответ от GPT: {answer}")
    except Exception as e:
        logging.error(f"❌ Ошибка при обращении к OpenAI: {e}")
    finally:
        await http_client.aclose()

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
