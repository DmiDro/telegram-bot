import psycopg2

# Подключение к базе данных PostgreSQL
try:
    conn = psycopg2.connect(
        dbname="telegram_bot_chg",
        user="postgres",
        password="postgres",  # 🔁 замени на свой пароль
        host="localhost"
    )
    print("✅ Успешное подключение к базе данных!")
    conn.close()

except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
