import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432))
}


async def get_tests_from_db() -> dict:
    conn = await asyncpg.connect(**DB_PARAMS)

    # Получаем все test_key из intro
    rows = await conn.fetch("SELECT test_key FROM intro")
    test_keys = [row["test_key"] for row in rows]

    tests = {}

    for test_key in test_keys:
        tests[test_key] = {"questions": []}
        try:
            questions = await conn.fetch(f"""
                SELECT question_index, question_text, option_index, option_text, option_value
                FROM {test_key}
                ORDER BY question_index, option_index
            """)

            current_q_index = -1
            current_question = {}

            for q in questions:
                if q["question_index"] != current_q_index:
                    if current_question:
                        tests[test_key]["questions"].append(current_question)
                    current_q_index = q["question_index"]
                    current_question = {
                        "text": q["question_text"],
                        "options": []
                    }

                current_question["options"].append({
                    "text": q["option_text"],
                    "value": q["option_value"]
                })

            if current_question:
                tests[test_key]["questions"].append(current_question)

        except Exception as e:
            print(f"⚠️ Ошибка при загрузке теста '{test_key}': {e}")

    await conn.close()
    return tests
