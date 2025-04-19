import os
import asyncio
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def test_connection():
    try:
        client = AsyncOpenAI(api_key=OPENAI_API_KEY, timeout=10.0)
        response = await client.models.list()
        logging.info("✅ OpenAI API доступен. Список моделей получен.")
        for model in response.data[:5]:  # Покажем первые 5 моделей
            logging.info(f"🧠 Модель: {model.id}")
    except Exception as e:
        logging.error(f"❌ Ошибка при обращении к OpenAI: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_connection())
