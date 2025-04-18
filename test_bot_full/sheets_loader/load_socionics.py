import os
import psycopg2
import gspread
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON").replace("\\", "/")

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def load_socionics_data():
    # Подключение к Google Sheets
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_JSON)
    sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet("socionics")
    rows = sheet.get_all_values()[1:]  # пропускаем заголовок

    # Подключение к PostgreSQL
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    # Очистка таблицы
    cur.execute("DELETE FROM socionics")

    # Вставка новых данных
    for row in rows:
        if len(row) >= 6:
            test_key, q_index, q_text, o_index, o_text, o_value = row
            cur.execute(
                """
                INSERT INTO socionics (
                    test_key, question_index, question_text,
                    option_index, option_text, option_value
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (test_key, int(q_index), q_text, int(o_index), o_text, o_value)
            )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Загружено из листа socionics")

if __name__ == "__main__":
    load_socionics_data()
