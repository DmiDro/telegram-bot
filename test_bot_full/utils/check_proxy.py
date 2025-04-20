import os
import logging
import openai
import socks
import socket

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# Получение переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROXY = os.getenv("OPENAI_PROXY")  # Пример: socks5://user:pass@host:port

if not OPENAI_API_KEY:
    logging.error("❌ Переменная окружения OPENAI_API_KEY не установлена.")
    exit(1)

if not OPENAI_PROXY:
    logging.error("❌ Переменная окружения OPENAI_PROXY не установлена.")
    exit(1)

# Парсинг данных прокси
try:
    from urllib.parse import urlparse
    proxy = urlparse(OPENAI_PROXY)
    proxy_host = proxy.hostname
    proxy_port = proxy.port
    proxy_username = proxy.username
    proxy_password = proxy.password
except Exception as e:
    logging.error(f"❌ Ошибка при разборе прокси: {e}")
    exit(1)

# Настройка прокси для сокетов
socks.set_default_proxy(
    socks.SOCKS5,
    proxy_host,
    proxy_port,
    username=proxy_username,
    password=proxy_password
)
socket.socket = socks.socksocket

# Настройка OpenAI
openai.api_key = OPENAI_API_KEY

# Отправка запроса
try:
    logging.info("📤 Отправляем запрос к OpenAI через прокси...")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Напиши мне короткий ответ"}],
        timeout=10
    )
    reply = response.choices[0].message.content.strip()
    logging.info(f"✅ Ответ от OpenAI: {reply}")
except Exception as e:
    logging.error(f"❌ Ошибка при обращении к OpenAI: {e}")
