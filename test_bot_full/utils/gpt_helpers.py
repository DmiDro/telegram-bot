import asyncpg
import os
import logging
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_heroes():
    try:
        logging.info("📥 Попытка загрузить героев из базы данных...")
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch("SELECT name, description FROM heroes")
        await conn.close()

        heroes = [{"name": row["name"], "description": row["description"]} for row in rows]
        logging.info(f"✅ Герои загружены: {len(heroes)} персонажей")
        return heroes

    except Exception as e:
        logging.error(f"❌ Ошибка при загрузке героев: {e}")
        return []
