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

def load_arch_res_data():
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_JSON)
    sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet("arch_res")
    rows = sheet.get_all_values()[1:]  # без заголовка

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("DELETE FROM arch_res")

    for row in rows:
        if len(row) >= 3:
            key, title, description = row[0], row[1], row[2]
            cur.execute(
                "INSERT INTO arch_res (key, title, description) VALUES (%s, %s, %s)",
                (key, title, description)
            )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Загружено из листа arch_res")

if __name__ == "__main__":
    load_arch_res_data()
