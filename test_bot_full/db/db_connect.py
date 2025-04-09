import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()import os
import psycopg2

def get_connection():
    # Используем переменные окружения, настроенные в Railway
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),       # Получаем хост из переменной окружения
        port=os.getenv("DB_PORT"),       # Получаем порт из переменной окружения
        dbname=os.getenv("DB_NAME"),     # Получаем имя базы данных из переменной окружения
        user=os.getenv("DB_USER"),       # Получаем имя пользователя из переменной окружения
        password=os.getenv("DB_PASSWORD")  # Получаем пароль из переменной окружения
    )

# Пример работы с базой данных
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

# Запуск теста подключения
if __name__ == "__main__":
    test_connection()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
