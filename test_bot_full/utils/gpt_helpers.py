# test_bot_full/utils/gpt_helpers.py

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

async def get_heroes():
    conn = await asyncpg.connect(**DB_PARAMS)
    rows = await conn.fetch("SELECT name, description FROM heroes")
    await conn.close()
    return [{"name": row["name"], "description": row["description"]} for row in rows]
