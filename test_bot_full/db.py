import os
import asyncpg
from datetime import datetime
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Переменные для подключения к базе данных
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Асинхронное подключение к базе данных
async def get_connection():
    return await asyncpg.connect(**DB_PARAMS)

# Функция для обработки значений None
def nullify(value):
    return value if value and str(value).strip() != "" else None

# Запись результата в базу данных
async def write_result_to_db(user_id: int, username: str, bot_results: dict, test_key: str):
    result = bot_results[user_id].get(test_key)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    field_map = {
        "archetype": "archetype",
        "emotional_maturity": "emotional_maturity",
        "socionics": "socionics",
        "character": "character"
    }
    field_to_update = field_map[test_key]

    conn = await get_connection()

    async with conn.transaction():
        await conn.execute(f"""
            INSERT INTO users (
                submission_date, test_time, user_id, username, subscription_status,
                forecast_time, unsubscribe_date, {field_to_update}
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (user_id) DO UPDATE SET
                submission_date = EXCLUDED.submission_date,
                test_time = EXCLUDED.test_time,
                username = EXCLUDED.username,
                subscription_status = 'YES',
                {field_to_update} = EXCLUDED.{field_to_update};
        """, date_str, time_str, user_id, username, "YES", "09:01", None, result)

    await conn.close()

# Получение всех test_key из таблицы intro
async def get_intro_titles():
    conn = await get_connection()
    try:
        rows = await conn.fetch("SELECT test_key, title FROM intro")
    finally:
        await conn.close()
    return {row['test_key']: row['title'] for row in rows}

# Получение всех ключей тестов (например, для меню)
async def get_tests_from_db():
    conn = await get_connection()
    rows = await conn.fetch("SELECT DISTINCT test_key FROM emotional_maturity")  # пример
    await conn.close()
    return [row['test_key'] for row in rows]

# Обновление статуса подписки
async def update_subscription_status(user_id: int, status: str):
    unsubscribe_date = datetime.now().strftime("%Y-%m-%d")

    conn = await get_connection()
    try:
        await conn.execute("""
            UPDATE users
            SET subscription_status = $1,
                unsubscribe_date = $2
            WHERE user_id = $3
        """, status, unsubscribe_date, user_id)
    finally:
        await conn.close()

# Получение списка подписанных пользователей
async def get_subscribed_users():
    conn = await get_connection()
    rows = await conn.fetch("""
        SELECT user_id FROM users
        WHERE subscription_status = 'YES'
    """)
    await conn.close()
    return [row['user_id'] for row in rows]
