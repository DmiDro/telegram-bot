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

# 🧠 Универсальная загрузка описания результата
async def get_result_description_from_db(test_key: str, result_code: str) -> dict:
    table_map = {
        "archetype": "arch_res",
        "emotional_maturity": "em_maturity_res",
        "socionics": "socionics_res",
        "character": "character_res"
    }

    table_name = table_map.get(test_key)
    if not table_name:
        print(f"❌ Не найдена таблица для test_key: {test_key}")
        return {}

    query = f"SELECT * FROM {table_name} WHERE key = $1"

    try:
        conn = await asyncpg.connect(**DB_PARAMS)
        row = await conn.fetchrow(query, result_code)
        await conn.close()

        if not row:
            print(f"❌ Результат {result_code} не найден в таблице {table_name}")
            return {}

        # Безопасное извлечение с fallback
        return {
            "name": row.get("name", result_code),
            "title": row.get("title", ""),
            "summary": row.get("summary", ""),
            "character": row.get("character", ""),
            "description": row.get("description", "")
        }

    except Exception as e:
        print(f"❌ Ошибка при получении описания результата: {e}")
        return {}
