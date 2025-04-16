# 📄 Файл: test_bot_full/db/write.py

import os
import asyncpg
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения (локально)
load_dotenv()

# Используем строку подключения DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")


# 🔌 Асинхронное подключение
async def get_connection():
    return await asyncpg.connect(DATABASE_URL)


# ✅ Универсальный null-обработчик
def nullify(value):
    return value if value and str(value).strip() != "" else None


# 💾 Запись результатов в таблицу users
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


# 🧠 Получение названий тестов (например, для меню)
async def get_intro_titles():
    conn = await get_connection()
    try:
        rows = await conn.fetch("SELECT test_key, title FROM intro")
        return {row['test_key']: row['title'] for row in rows}
    finally:
        await conn.close()


# 📋 Список тестов
async def get_tests_from_db():
    conn = await get_connection()
    try:
        rows = await conn.fetch("SELECT DISTINCT test_key FROM intro")
        return [row['test_key'] for row in rows]
    finally:
        await conn.close()


# 🔁 Обновление подписки
async def update_subscription_status(user_id: int, status: str):
    unsubscribe_date = datetime.now().strftime("%Y-%m-%d") if status == "NO" else None

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


# 📤 Список активных пользователей
async def get_subscribed_users():
    conn = await get_connection()
    try:
        rows = await conn.fetch("""
            SELECT user_id FROM users
            WHERE subscription_status = 'YES'
        """)
        return [row['user_id'] for row in rows]
    finally:
        await conn.close()
