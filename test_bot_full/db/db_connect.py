import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env (только локально, на Railway не нужен)

def get_connection():
    # Подключение к PostgreSQL через переменные окружения
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def test_connection():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM public.users LIMIT 10;")
        rows = cursor.fetchall()

        for row in rows:
            print(row)

        cursor.close()
        connection.close()
    except Exception as e:
        print("Ошибка подключения:", e)

if __name__ == "__main__":
    test_connection()
