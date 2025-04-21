import asyncio
import os
import logging
from aiohttp_socks import open_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

PROXY_URL = os.getenv("OPENAI_PROXY")  # Используем ту же переменную

async def main():
    logging.info(f"🔌 Прокси: {PROXY_URL}")

    try:
        # Устанавливаем соединение через SOCKS5 прокси
        reader, writer = await open_connection(
            proxy_url=PROXY_URL,
            host='tcpbin.com',  # публичный echo-сервер
            port=4242
        )
        logging.info("📡 Соединение установлено!")

        # Отправляем привет
        message = "привет\n"
        writer.write(message.encode())
        await writer.drain()

        logging.info(f"📤 Отправлено: {message.strip()}")

        # Читаем ответ
        data = await reader.readline()
        logging.info(f"📥 Ответ от сервера: {data.decode().strip()}")

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        logging.exception("❌ Ошибка соединения через прокси:")

if __name__ == "__main__":
    asyncio.run(main())
