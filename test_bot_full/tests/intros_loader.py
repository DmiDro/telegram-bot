# test_bot_full/tests/intros_loader.py

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

async def get_test_intros():
    conn = await asyncpg.connect(**DB_PARAMS)
    rows = await conn.fetch("SELECT test_key, title FROM intro")
    await conn.close()
    return {row["test_key"]: row["title"] for row in rows}
