import asyncio
import os
import logging
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

API_KEY = os.getenv("OPENAI_API_KEY")
PROXY_URL = os.getenv("OPENAI_PROXY")

async def main():
    logging.info(f"🔌 Используем прокси: {PROXY_URL}")
    connector = ProxyConnector.from_url(PROXY_URL)

    async with ClientSession(connector=connector) as session:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        json = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Привет, ты жив?"}]
        }

        try:
            logging.info("📤 Отправка запроса к OpenAI...")
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json) as resp:
                logging.info(f"📥 Status: {resp.status}")
                if resp.status != 200:
                    logging.error(f"❌ Ошибка ответа: {await resp.text()}")
                    return
                data = await resp.json()
                answer = data["choices"][0]["message"]["content"].strip()
                print("✅ Ответ от GPT:", answer)
        except Exception as e:
            logging.exception("❌ Ошибка при запросе к OpenAI:")

if __name__ == "__main__":
    asyncio.run(main())
