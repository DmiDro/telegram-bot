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

logging.info(f"🔌 OPENAI_PROXY: {repr(OPENAI_PROXY)}")

async def main():
    logging.info("📤 Подготовка клиента httpx с прокси...")

    # Настройка таймаутов
    timeout = httpx.Timeout(30.0, connect=10.0)

    # Настройка прокси
    proxies = {"all://": OPENAI_PROXY} if OPENAI_PROXY else None
    async with httpx.AsyncClient(proxies=proxies, timeout=timeout) as http_client:
        logging.info("🤖 Инициализация клиента OpenAI...")
        client = AsyncOpenAI(api_key=OPENAI_API_KEY, http_client=http_client)

        try:
            logging.info("✉️ Отправка запроса к GPT...")
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": "Напиши мне короткий ответ"}]
                ),
                timeout=25.0
            )
            answer = response.choices[0].message.content.strip()
            logging.info(f"✅ Ответ от GPT: {answer}")
        except asyncio.TimeoutError:
            logging.error("⏰ Таймаут ожидания ответа от OpenAI.")
        except Exception as e:
            logging.error(f"❌ Общая ошибка при обращении к OpenAI: {e}")
        finally:
            logging.info("🔒 HTTP-клиент закрыт.")

if __name__ == "__main__":
    asyncio.run(main())
