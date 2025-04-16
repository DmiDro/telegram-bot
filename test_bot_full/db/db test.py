import os
import psycopg2
from dotenv import load_dotenv

# ⛺ Локальная разработка: подгружаем .env
load_dotenv()

try:
    # 🔐 Подключение по переменной окружения DATABASE_URL
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    print("✅ Успешное подключение к базе данных!")
    conn.close()

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
