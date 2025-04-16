import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Локально подхватит .env, на Railway переменные уже в окружении

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

# ✅ Дополнительная проверка соединения
def test_connection():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.users LIMIT 10;")
        rows = cur.fetchall()
        for row in rows:
            print(row)
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ Ошибка подключения к базе данных:", e)

# Локальный тест
if __name__ == "__main__":
    test_connection()
