import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 📚 Получение списка героев из таблицы heroes
async def get_hero_list() -> list[dict]:
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch("SELECT name, description, link FROM heroes")
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"❌ Ошибка при загрузке героев: {e}")
        return []
    finally:
        if conn:
            await conn.close()
