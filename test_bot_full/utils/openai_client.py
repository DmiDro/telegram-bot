import os
import logging
import asyncio
from openai import OpenAI, AsyncOpenAI
from openai._types import NotGiven

# 🔐 Ожидаем, что ключ будет выставлен как переменная среды в Railway
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]  # Railway → Set in Variables
OPENAI_PROXY = os.environ.get("OPENAI_PROXY")  # Proxy (если задан)

# Синхронный клиент (fallback)
sync_client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.openai.com/v1",
    proxies={"http": OPENAI_PROXY, "https": OPENAI_PROXY} if OPENAI_PROXY else None
)

# Асинхронный клиент (основной)
async_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.openai.com/v1",
    http_client=AsyncOpenAI.HTTPClient(
        proxy=OPENAI_PROXY if OPENAI_PROXY else NotGiven()
    )
)

# Универсальная функция: сначала пробует async, если ошибка — fallback на sync
async def generate_response(prompt: str, model: str = "gpt-4o") -> str:
    try:
        response = await async_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        return response.choices[0].message.content.strip()

    except Exception as e_async:
        logging.error(f"⚠️ AsyncOpenAI ошибка: {e_async}. Пробуем fallback через sync.")

        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: sync_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt.strip()}]
                )
            )
            return response.choices[0].message.content.strip()

        except Exception as e_sync:
            logging.critical(f"❌ Fallback (sync) тоже не сработал: {e_sync}")
            return "⚠️ Не удалось получить ответ от OpenAI."
