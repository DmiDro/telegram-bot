import os
import psycopg2
from dotenv import load_dotenv

# Загружаем переменные окружения из .env (только для локальной разработки)
load_dotenv()

def get_connection():
    """
    Создаёт подключение к PostgreSQL с использованием DATABASE_URL.
    Railway автоматически предоставляет эту переменную в окружении.
    """
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def test_connection():
    """
    Простой тест подключения к БД.
    Показывает первые 10 строк из таблицы users.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.users LIMIT 10;")
        rows = cur.fetchall()
        for row in rows:
            print(row)
        cur.close()
        conn.close()
        print("✅ Подключение успешно")
    except Exception as e:
        print("❌ Ошибка подключения к базе данных:", e)

# Локальный тест
if __name__ == "__main__":
    test_connection()
