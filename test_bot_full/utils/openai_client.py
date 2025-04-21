import os
import logging
import asyncio
import httpx

# Адрес FastAPI-прокси
PROXY_ENDPOINT = os.getenv("GPT_PROXY_ENDPOINT", "http://45.155.102.141:8000/chat")

# HTTP-клиент
http_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))

# Генерация ответа
async def generate_response(prompt: str, model: str = "gpt-4o") -> str:
    prompt_id = prompt.strip()[:60]
    try:
        logging.info(f"📤 FastAPI-прокси: отправка prompt ({prompt_id})")
        response = await http_client.post(
            PROXY_ENDPOINT,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt.strip()}]
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("result", "⚠️ Ответ пуст.").strip()

    except Exception as e:
        logging.critical(f"❌ Ошибка при обращении к FastAPI-прокси: {e}")
        return "⚠️ Не удалось получить ответ от GPT-прокси."
