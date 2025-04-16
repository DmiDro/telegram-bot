from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.results import get_tests_from_db, get_intro_titles
from db.write import get_connection


# 📌 Получение списка уже пройденных тестов пользователем
async def get_completed_tests(user_id: int) -> set:
    print(f"🔍 Получаем пройденные тесты для user_id = {user_id}")
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
        print("🟨 Пользователь не найден в таблице users")
        return set()

    completed = {
        key for key, value in zip(
            ["archetype", "emotional_maturity", "socionics", "character"],
            row
        ) if value
    }
    print(f"✅ Пройденные тесты: {completed}")
    return completed


# 📌 Клавиатура меню с кнопками тестов
async def menu_keyboard(user_id: int = None) -> InlineKeyboardMarkup:
    print("🟡 menu_keyboard вызван. user_id =", user_id)

    try:
        test_intros = await get_intro_titles()
        print("📌 Заголовки тестов (intro):", test_intros)

        test_keys = await get_tests_from_db()
        print("📌 Все ключи тестов:", test_keys)

        if user_id:
            completed = await get_completed_tests(user_id)
            print("📌 Фильтруем уже пройденные:", completed)
            test_keys = [key for key in test_keys if key not in completed]
            print("📌 Оставшиеся тесты:", test_keys)

        buttons = [
            [
                InlineKeyboardButton(
                    text=test_intros.get(key, key),
                    callback_data=f"start_{key}"
                )
            ]
            for key in test_keys
        ]

        print("📌 Кнопки для меню:", buttons)

        if not buttons:
            print("⚠️ Нет доступных тестов. Добавляем заглушку.")
            buttons = [[InlineKeyboardButton(text="🔁 Пройти заново", callback_data="start_emotional_maturity")]]

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    except Exception as e:
        print("❌ Ошибка в menu_keyboard:", e)
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚠️ Ошибка загрузки меню", callback_data="ignore")]
        ])


# 📌 Клавиатура с вариантами ответов
def answer_keyboard(test_key: str, question_index: int, question_data: dict) -> InlineKeyboardMarkup:
    print(f"🟠 Формируем клавиатуру для вопроса {question_index} в тесте '{test_key}'")
    print("🧾 Вопрос:", question_data)
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

        padded_text = f" {text} "  # em-spaces
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
