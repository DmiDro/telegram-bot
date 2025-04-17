# 📄 Файл: test_bot_full/db/results.py

import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# Используем строку подключения через DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# 🧠 Получение интро-кнопок из таблицы intro
async def get_intro_titles() -> dict:
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT test_key, title FROM intro")
    await conn.close()
    return {row['test_key']: row['title'] for row in rows}

# 📋 Получение всех тестов (ключей) из таблицы intro
async def get_tests_from_db() -> list:
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT test_key FROM intro")
    await conn.close()
    return [row['test_key'] for row in rows]
