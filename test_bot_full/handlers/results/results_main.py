# 📄 test_bot_full/handlers/results/results_main.py

import logging
from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest

from test_bot_full.utils.keyboards import menu_keyboard
from test_bot_full.handlers.results.interpreters import interpret_results
from test_bot_full.handlers.results.state import bot_results
from test_bot_full.db.write import write_result_to_db
from test_bot_full.db.descriptions import get_result_description_from_db
from test_bot_full.handlers.start import user_menu_messages

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

    logging.info(f"[RESULT] Завершён тест: {test_key} — Ответы: {answers}")

    result = interpret_results(test_key, answers, {})
    logging.info(f"[RESULT] Подсчитан результат: {result}")

    description_data = await get_result_description_from_db(test_key, result)
    logging.info(f"[RESULT] Описание результата получено: {bool(description_data)}")

    if not description_data:
        await message.answer("❌ Описание результата не найдено.")
        return

    try:
        text = format_result_output(test_key, description_data)
        await message.answer(text, parse_mode="HTML")
    except TelegramBadRequest as e:
        logging.warning(f"⚠️ Ошибка при отправке описания результата: {e}")
        await message.answer("⚠️ Не удалось отобразить результат.")

    # Сохраняем результат
    if user_id not in bot_results:
        bot_results[user_id] = {}
    bot_results[user_id][test_key] = result

    await write_result_to_db(
        user_id=user_id,
        username=user.full_name,
        bot_results=bot_results,
        test_key=test_key
    )

    # Обновляем или отправляем новое меню
    keyboard = await menu_keyboard()
    text = "Вы можете пройти следующий тест:"

    if user_id in user_menu_messages:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=user_menu_messages[user_id],
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            logging.info(f"[RESULT] Меню обновлено у пользователя {user_id}")
            return
        except Exception as e:
            logging.warning(f"⚠️ Не удалось обновить меню после теста: {e}")

    sent = await message.answer(text, reply_markup=keyboard)
    user_menu_messages[user_id] = sent.message_id
    logging.info(f"[RESULT] Отправлено новое меню пользователю {user_id}")
