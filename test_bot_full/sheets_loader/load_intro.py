import os
import psycopg2
import gspread
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON").replace("\\", "/")

DB_PARAMS = {
    "dbname": "telegram_bot_chg",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432
}

def load_intro_data():
    # Подключение к Google Sheets
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_JSON)
    sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet("intro")
    rows = sheet.get_all_values()[1:]  # пропускаем заголовок

    # Подключение к PostgreSQL
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    # Очистка таблицы
    cur.execute("DELETE FROM intro")

    # Вставка новых данных
    for row in rows:
        if len(row) >= 2:
            test_key, title = row[0], row[1]
            cur.execute(
                "INSERT INTO intro (test_key, title) VALUES (%s, %s)",
                (test_key, title)
            )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Загружено из листа intro")

if __name__ == "__main__":
    load_intro_data()
