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

def load_emotional_maturity():
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_JSON)
    sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet("emotional_maturity")
    rows = sheet.get_all_values()[1:]  # без заголовков

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("DELETE FROM emotional_maturity")

    for row in rows:
        if len(row) >= 6:
            cur.execute(
                """
                INSERT INTO emotional_maturity 
                (test_key, question_index, question_text, option_index, option_text, option_value)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (row[0], int(row[1]), row[2], int(row[3]), row[4], int(row[5]))
            )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Загружено из листа emotional_maturity")

if __name__ == "__main__":
    load_emotional_maturity()
