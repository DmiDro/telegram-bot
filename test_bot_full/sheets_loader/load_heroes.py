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
    "port": os.getenv("DB_PORT"),
}

def load_heroes_data():
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_JSON)
    sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet("heroes")
    rows = sheet.get_all_values()[1:]

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("DELETE FROM heroes")

    for row in rows:
        if len(row) >= 3:
            name, description, link = row[0], row[1], row[2]
            cur.execute(
                "INSERT INTO heroes (name, description, link) VALUES (%s, %s, %s)",
                (name, description, link)
            )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Загружено из листа heroes")

if __name__ == "__main__":
    load_heroes_data()
