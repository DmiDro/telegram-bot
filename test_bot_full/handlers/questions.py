# test_bot_full/handlers/questions.py

from aiogram import Router, types, F
from test_bot_full.tests.loader import get_tests_from_db
from test_bot_full.utils.keyboards import answer_keyboard

router = Router()
user_answers = {}

# === НАЧАЛО ТЕСТА ===
@router.callback_query(F.data.startswith("start_"))
async def start_test(callback: types.CallbackQuery):
    test_key = callback.data.replace("start_", "")
    user_id = callback.from_user.id
    user_answers[user_id] = {"test": test_key, "answers": []}

    try:
        await callback.message.delete()
    except Exception as e:
        print("⚠️ Не удалось удалить сообщение:", e)

    tests = await get_tests_from_db()
    first_question = tests[test_key]["questions"][0]
    print("DEBUG TEST DATA:", first_question)

    await callback.message.answer(
        first_question["text"],
        reply_markup=answer_keyboard(test_key, 0, first_question)
    )

# === ОБРАБОТКА ОТВЕТОВ ===
@router.callback_query(F.data.startswith("answer|"))
async def handle_answer(callback: types.CallbackQuery):
    try:
        _, test_key, q_index, answer_idx = callback.data.split("|")
        user_id = callback.from_user.id
        q_index, answer_idx = int(q_index), int(answer_idx)

        tests = await get_tests_from_db()
        question = tests[test_key]["questions"][q_index]
        option = question["options"][answer_idx]
        answer_value = option.get("value", answer_idx)

        user_answers[user_id]["answers"].append(answer_value)

        try:
            await callback.message.delete()
        except Exception as e:
            print("⚠️ Не удалось удалить сообщение:", e)

        next_index = q_index + 1
        if next_index < len(tests[test_key]["questions"]):
            next_question = tests[test_key]["questions"][next_index]
            await callback.message.answer(
                next_question["text"],
                reply_markup=answer_keyboard(test_key, next_index, next_question)
            )
        else:
            from test_bot_full.handlers.results.results_main import finish_test
            await finish_test(callback.message, user_id, callback.from_user, user_answers)

    except Exception as e:
        await callback.message.answer("Произошла ошибка при обработке ответа.")
        import traceback
        traceback.print_exc()
