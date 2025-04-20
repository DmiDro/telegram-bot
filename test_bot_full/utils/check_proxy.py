import asyncio
import logging
import os
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

API_KEY = os.getenv("OPENAI_API_KEY")
PROXY_URL = os.getenv("OPENAI_PROXY")

async def main():
    logging.info(f"🔌 Используем прокси: {PROXY_URL}")

    connector = ProxyConnector.from_url(PROXY_URL)
    async with ClientSession(connector=connector) as session:
        logging.info("✉️ Отправка запроса к OpenAI...")
        headers = {"Authorization": f"Bearer {API_KEY}"}
        json = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Привет!"}]
        }

        async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json) as resp:
            if resp.status != 200:
                logging.error(f"❌ Ошибка: {resp.status} — {await resp.text()}")
                return

            data = await resp.json()
            answer = data["choices"][0]["message"]["content"]
            logging.info(f"✅ Ответ от GPT: {answer}")

if __name__ == "__main__":
    asyncio.run(main())
