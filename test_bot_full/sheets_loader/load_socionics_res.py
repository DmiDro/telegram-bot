import os
import psycopg2
import gspread
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")  # Обрати внимание: "GOOGLE_SHEETS_ID"
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON").replace("\\", "/")

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def load_socionics_res_data():
    # Google Sheets
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_JSON)
    sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet("socionics_res")
    rows = sheet.get_all_values()[1:]  # без заголовков

    # PostgreSQL
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("DELETE FROM socionics_res")

    for row in rows:
        if len(row) >= 5:
            key, name, summary, character, description = row
            cur.execute("""
                INSERT INTO socionics_res (key, name, summary, character, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (key, name, summary, character, description))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Загружено из листа socionics_res")

if __name__ == "__main__":
    load_socionics_res_data()
