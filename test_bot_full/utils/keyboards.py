from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from test_bot_full.db.results import get_tests_from_db, get_intro_titles


# 📌 Меню с кнопками выбора тестов (без кнопки отписки)
async def menu_keyboard() -> InlineKeyboardMarkup:
    test_intros = await get_intro_titles()
    test_keys = await get_tests_from_db()

    buttons = [
        [
            InlineKeyboardButton(
                text=test_intros.get(key, key),  # Название из интро
                callback_data=f"start_{key}"
            )
        ]
        for key in test_keys
    ]

    # ❌ Больше нет кнопки "Отказаться от прогноза"
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# 📌 Клавиатура с вариантами ответов на вопрос
def answer_keyboard(test_key: str, question_index: int, question_data: dict) -> InlineKeyboardMarkup:
    buttons = []

    print(f"DEBUG: Вопрос {question_index} → {question_data}")  # 🐞 Отладка

    options = question_data.get("options")
    if not options:
        print(f"⚠️ У вопроса нет вариантов ответа: {question_data}")
        return InlineKeyboardMarkup(inline_keyboard=[])

    for i, opt in enumerate(options):
        if isinstance(opt, dict):
            text = opt.get("text", str(opt))
        elif isinstance(opt, tuple):
            text = opt[0]
        else:
            text = str(opt)

        buttons.append([
            InlineKeyboardButton(
                text=text,
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
