from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db.results import get_tests_from_db, get_intro_titles
from db.write import get_connection  # ✅ Исправленный импорт


# 📌 Получение списка уже пройденных тестов пользователем
async def get_completed_tests(user_id: int) -> set:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT archetype, emotional_maturity, socionics, character
        FROM users
        WHERE user_id = %s
    """, (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return set()

    return {
        key for key, value in zip(
            ["archetype", "emotional_maturity", "socionics", "character"],
            row
        ) if value
    }


# 📌 Клавиатура меню с кнопками тестов
async def menu_keyboard(user_id: int = None) -> InlineKeyboardMarkup:
    test_intros = await get_intro_titles()
    test_keys = await get_tests_from_db()

    if user_id:
        completed = await get_completed_tests(user_id)
        test_keys = [key for key in test_keys if key not in completed]

    buttons = [
        [
            InlineKeyboardButton(
                text=test_intros.get(key, key),
                callback_data=f"start_{key}"
            )
        ]
        for key in test_keys
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# 📌 Клавиатура с вариантами ответов
def answer_keyboard(test_key: str, question_index: int, question_data: dict) -> InlineKeyboardMarkup:
    print(f"DEBUG: Вопрос {question_index} → {question_data}")
    options = question_data.get("options")

    if not options:
        print(f"⚠️ У вопроса нет вариантов ответа: {question_data}")
        return InlineKeyboardMarkup(inline_keyboard=[])

    buttons = []
    for i, opt in enumerate(options):
        if isinstance(opt, dict):
            text = opt.get("text", str(opt))
        elif isinstance(opt, tuple):
            text = opt[0]
        else:
            text = str(opt)

        padded_text = f" {text} "  # em-spaces для красивого вида
        buttons.append([
            InlineKeyboardButton(
                text=padded_text,
                callback_data=f"answer|{test_key}|{question_index}|{i}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# 📌 Клавиатура подтверждения отписки
def unsubscribe_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="confirm_unsubscribe")],
        [InlineKeyboardButton(text="❌ Нет", callback_data="cancel_unsubscribe")]
    ])
