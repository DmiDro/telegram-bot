# 📄 Файл: test_bot_full/db/results.py
# Этот файл отвечает за загрузку полного описания результата теста из PostgreSQL,
# включая заголовок, краткое описание, героя и полное описание результата.

import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432))
}

# 🧠 Получение интро-кнопок из таблицы intro
async def get_intro_titles() -> dict:
    conn = await asyncpg.connect(**DB_PARAMS)
    rows = await conn.fetch("SELECT test_key, title FROM intro")
    await conn.close()
    return {row['test_key']: row['title'] for row in rows}

# 📋 Получение всех тестов (ключей) из таблицы emotional_maturity
async def get_tests_from_db() -> list:
    conn = await asyncpg.connect(**DB_PARAMS)
    rows = await conn.fetch("SELECT test_key FROM intro")
    await conn.close()
    return [row['test_key'] for row in rows]

