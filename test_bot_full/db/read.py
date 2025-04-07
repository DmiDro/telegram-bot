import psycopg2
from test_bot_full.db.write import get_connection

async def is_first_launch(user_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is None  # True — если записи нет
