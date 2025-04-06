from test_bot_full.db.db_connect import get_connection

def insert_or_update_user(data: dict):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users_results (
            user_id, full_name, subscribe,
            first_test_date, first_test_time,
            forecast_time, unsubscribe_date,
            archetype_key, maturity_key, socionics_key, character_key
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            subscribe = EXCLUDED.subscribe,
            forecast_time = EXCLUDED.forecast_time,
            unsubscribe_date = EXCLUDED.unsubscribe_date,
            archetype_key = EXCLUDED.archetype_key,
            maturity_key = EXCLUDED.maturity_key,
            socionics_key = EXCLUDED.socionics_key,
            character_key = EXCLUDED.character_key;
    """, (
        data["user_id"],
        data["full_name"],
        data.get("subscribe", True),
        data.get("first_test_date"),
        data.get("first_test_time"),
        data.get("forecast_time", "09:01:00"),
        data.get("unsubscribe_date"),
        data.get("archetype_key"),
        data.get("maturity_key"),
        data.get("socionics_key"),
        data.get("character_key"),
    ))

    conn.commit()
    cur.close()
    conn.close()
