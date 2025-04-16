# test_bot_full/tests/intros_loader.py

import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_test_intros():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT test_key, title FROM intro")
    await conn.close()
    return {row["test_key"]: row["title"] for row in rows}

