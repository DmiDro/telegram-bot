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

def load_character_res_data():
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_JSON)
    sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet("character_res")
    rows = sheet.get_all_values()[1:]

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("DELETE FROM character_res")

    for row in rows:
        if len(row) >= 3:
            key, title, description = row
            cur.execute("""
                INSERT INTO character_res (key, title, description)
                VALUES (%s, %s, %s)
            """, (key, title, description))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Загружено из листа character_res")

if __name__ == "__main__":
    load_character_res_data()
