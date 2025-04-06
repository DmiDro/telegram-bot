import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

async def get_heroes():
    conn = await asyncpg.connect(**DB_PARAMS)
    rows = await conn.fetch("SELECT name, description, link FROM heroes")
    await conn.close()

    return [
        {
            "name": row["name"],
            "description": row["description"],
            "link": row["link"]
        }
        for row in rows
    ]
