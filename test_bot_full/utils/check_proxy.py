import asyncio
import os
import logging
from aiohttp import ClientSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# URL прокси-сервера (наш FastAPI-прокси)
PROXY_SERVER_URL = os.getenv("FORWARDER_URL", "http://45.155.102.141:8000/chat")

async def main():
    logging.info(f"\U0001f50c Тестируем FastAPI-прокси по адресу: {PROXY_SERVER_URL}")

    async with ClientSession() as session:
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Привет, ответь мне красиво"}]
        }

        try:
            logging.info("\U0001f4e4 Отправка запроса к FastAPI-прокси...")
            async with session.post(PROXY_SERVER_URL, json=payload) as resp:
                logging.info(f"\U0001f4e5 Статус ответа: {resp.status}")
                data = await resp.json()
                print("\u2705 Ответ от FastAPI-прокси:", data["choices"][0]["message"]["content"])
        except Exception as e:
            logging.exception("❌ Ошибка при обращении к FastAPI-прокси:")

if __name__ == "__main__":
    asyncio.run(main())
