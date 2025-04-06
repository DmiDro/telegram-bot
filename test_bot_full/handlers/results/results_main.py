from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest

from test_bot_full.utils.keyboards import menu_keyboard
from test_bot_full.handlers.results.interpreters import interpret_results
from test_bot_full.handlers.results.state import bot_results
from test_bot_full.handlers.results.message_state import result_messages
from test_bot_full.db.write import write_result_to_db
from test_bot_full.db.descriptions import get_result_description_from_db

router = Router()

def format_result_output(test_key: str, data: dict) -> str:
    def indent(text):
        return f"<i>{' ' * 5}{text}</i>"

    if test_key == "socionics":
        name = f"<b>{data.get('name', '')}</b>"
        summary = data.get("summary", "").replace("\n", " ")
        description = data.get("description", "").replace("\n", " ")
        return f"{name}\n\n{indent(summary)}\n\n{indent(description)}"

    else:
        title = f"<b>{data.get('title', '')}</b>"
        description = data.get("description", "").replace("\n", " ")
        return f"{title}\n\n{indent(description)}"

async def finish_test(message: types.Message, user_id: int, user: types.User, user_answers: dict):
    test_key = user_answers[user_id]["test"]
    answers = user_answers[user_id]["answers"]

    print(f"[DEBUG] test_key: {test_key}")
    print(f"[DEBUG] answers: {answers}")

    result = interpret_results(test_key, answers, {})
    print(f"[DEBUG] result: {result}")

    description_data = await get_result_description_from_db(test_key, result)
    print(f"[DEBUG] description found: {description_data}")

    if not description_data:
        await message.answer("❌ Описание результата не найдено.", allow_reactions=False)
        return

    try:
        text = format_result_output(test_key, description_data)
        await message.answer(text, parse_mode="HTML", allow_reactions=False)
    except TelegramBadRequest as e:
        print(f"⚠️ Ошибка при отправке описания результата: {e}")
        await message.answer("⚠️ Не удалось отобразить результат.", allow_reactions=False)

    if user_id not in bot_results:
        bot_results[user_id] = {}
    bot_results[user_id][test_key] = result

    await write_result_to_db(
        user_id=user_id,
        username=user.full_name,
        bot_results=bot_results,
        test_key=test_key
    )

    await message.answer(
        "Вы можете пройти следующий тест:",
        reply_markup=await menu_keyboard(),
        allow_reactions=False
    )
