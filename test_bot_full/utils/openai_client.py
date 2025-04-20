import os
import logging
import asyncio
import httpx
from openai import AsyncOpenAI

# 🔐 Railway → Set in Variables
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_PROXY = os.environ.get("OPENAI_PROXY", "").strip()

# 👉 Обработка socks5h:// → socks5://
if OPENAI_PROXY.startswith("socks5h://"):
    OPENAI_PROXY = "socks5://" + OPENAI_PROXY[len("socks5h://"):]

# ✅ httpx с прокси
http_client = httpx.AsyncClient(
    proxies={"all://": OPENAI_PROXY} if OPENAI_PROXY else None,
    timeout=httpx.Timeout(30.0)
)

# Асинхронный клиент OpenAI
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    http_client=http_client
)

# Генерация ответа
async def generate_response(prompt: str, model: str = "gpt-4o") -> str:
    prompt_id = prompt.strip()[:60]
    try:
        logging.info(f"📤 OpenAI: отправка prompt ({prompt_id})")
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logging.critical(f"❌ Ошибка OpenAI: {e}")
        return "⚠️ Не удалось получить ответ от OpenAI."
