import os
import logging
import asyncio
from openai import OpenAI, AsyncOpenAI
from openai._httpx import AsyncHttpxClient

# 🔐 Railway → Set in Variables
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_PROXY = os.environ.get("OPENAI_PROXY")

# Синхронный клиент
sync_client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.openai.com/v1",
    proxies={"http": OPENAI_PROXY, "https": OPENAI_PROXY} if OPENAI_PROXY else None
)

# Асинхронный клиент
async_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.openai.com/v1",
    http_client=AsyncHttpxClient(proxy=OPENAI_PROXY) if OPENAI_PROXY else None
)

# Генерация ответа с fallback
async def generate_response(prompt: str, model: str = "gpt-4o") -> str:
    prompt_id = prompt.strip()[:60]
    try:
        logging.info(f"📤 AsyncOpenAI: отправка prompt ({prompt_id})")
        response = await async_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        return response.choices[0].message.content.strip()

    except Exception as e_async:
        logging.error(f"⚠️ AsyncOpenAI ошибка: {e_async} — fallback на sync.")

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
            logging.critical(f"❌ Sync fallback тоже упал: {e_sync}")
            return "⚠️ Не удалось получить ответ от OpenAI."
