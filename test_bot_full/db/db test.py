import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Работает локально, Railway использует переменные окружения напрямую

try:
    # Подключение через строку DATABASE_URL
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    print("✅ Успешное подключение к базе данных!")
    conn.close()

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
