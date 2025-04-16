import asyncpg
import os
from dotenv import load_dotenv

# Локальная загрузка переменных окружения
load_dotenv()

# Railway автоматически подставляет DATABASE_URL в окружение
DATABASE_URL = os.getenv("DATABASE_URL")

# 📤 Загрузка героев для генерации рекомендаций
async def get_heroes():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch("SELECT name, description FROM heroes")
        await conn.close()

        return [{"name": row["name"], "description": row["description"]} for row in rows]
    except Exception as e:
        print(f"❌ Ошибка при загрузке героев: {e}")
        return []
