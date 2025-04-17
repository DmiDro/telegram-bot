import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_heroes():
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch("SELECT name, description, link FROM heroes")
        return [
            {
                "name": row["name"],
                "description": row["description"],
                "link": row["link"]
            }
            for row in rows
        ]
    except Exception as e:
        print(f"❌ Ошибка при загрузке героев: {e}")
        return []
    finally:
        if conn:
            await conn.close()
