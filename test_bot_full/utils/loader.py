# Загрузка героев из базы данных PostgreSQL
import asyncpg

async def load_heroes_from_db(pool):
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT name, description, link FROM heroes")
        return [{"name": r["name"], "description": r["description"], "link": r["link"]} for r in rows]
