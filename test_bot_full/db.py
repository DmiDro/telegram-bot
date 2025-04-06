import psycopg2
from datetime import datetime

DB_PARAMS = {
    "dbname": "telegram_bot_chg",
    "user": "postgres",
    "password": "postgres",  # Заменить на реальный пароль  
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_PARAMS)


def nullify(value):
    return value if value and str(value).strip() != "" else None


async def write_result_to_db(user_id: int, username: str, bot_results: dict, test_key: str):
    result = bot_results[user_id].get(test_key)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    field_map = {
        "archetype": "archetype",
        "emotional_maturity": "emotional_maturity",
        "socionics": "socionics",
        "character": "character"
    }
    field_to_update = field_map[test_key]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        INSERT INTO users (
            submission_date, test_time, user_id, username, subscription_status,
            forecast_time, unsubscribe_date, {field_to_update}
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            submission_date = EXCLUDED.submission_date,
            test_time = EXCLUDED.test_time,
            username = EXCLUDED.username,
            subscription_status = 'YES',
            {field_to_update} = EXCLUDED.{field_to_update};
    """, (
        date_str, time_str, user_id, username, "YES", "09:01", None, result
    ))

    conn.commit()
    cur.close()
    conn.close()

# Получение всех test_key из таблицы intro
async def get_intro_titles():
    conn = await asyncpg.connect(**DB_PARAMS)
    rows = await conn.fetch("SELECT test_key, title FROM intro")
    await conn.close()
    return {row['test_key']: row['title'] for row in rows}

# Получение всех ключей тестов (например, для меню)
async def get_tests_from_db():
    conn = await asyncpg.connect(**DB_PARAMS)
    rows = await conn.fetch("SELECT DISTINCT test_key FROM emotional_maturity")  # пример
    await conn.close()
    return [row['test_key'] for row in rows]




async def update_subscription_status(user_id: int, status: str):
    unsubscribe_date = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET subscription_status = %s,
            unsubscribe_date = %s
        WHERE user_id = %s
    """, (status, unsubscribe_date, user_id))

    conn.commit()
    cur.close()
    conn.close()


async def get_subscribed_users():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id FROM users
        WHERE subscription_status = 'YES'
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [row[0] for row in rows]
