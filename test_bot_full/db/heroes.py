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

# 📚 Получение списка героев из таблицы heroes
async def get_hero_list() -> list[dict]:
    conn = None
    try:
        conn = await asyncpg.connect(**DB_PARAMS)
        rows = await conn.fetch("SELECT name, description, link FROM heroes")
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"❌ Ошибка при загрузке героев: {e}")
        return []
    finally:
        if conn:
            await conn.close()
