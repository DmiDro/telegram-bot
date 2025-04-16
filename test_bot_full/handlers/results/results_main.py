# 📄 test_bot_full/handlers/results/results_main.py

import logging
from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest

from utils.keyboards import menu_keyboard
from handlers.results.interpreters import interpret_results
from db.write import write_result_to_db, update_subscription_status
from db.descriptions import get_result_description_from_db
from handlers.start import user_menu_messages
from handlers.results.message_state import result_messages


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

    text = format_result_output(test_key, description_data)

    existing_result_message = result_messages.get(user_id, {}).get(test_key)

    if existing_result_message:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=existing_result_message,
                text=text,
                parse_mode="HTML"
            )
            logging.info(f"[RESULT] Результат обновлён у пользователя {user_id}")
        except Exception as e:
            logging.warning(f"⚠️ Не удалось обновить старый результат: {e}")
            sent = await message.answer(text, parse_mode="HTML")
            result_messages.setdefault(user_id, {})[test_key] = sent.message_id
    else:
        sent = await message.answer(text, parse_mode="HTML")
        result_messages.setdefault(user_id, {})[test_key] = sent.message_id
        logging.info(f"[RESULT] Новый результат отправлен пользователю {user_id}")

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
    keyboard = await menu_keyboard(user_id)

    if not keyboard.inline_keyboard:  # если список кнопок пуст
        text = (
            "🎉 <b>Ты прошёл все тесты!</b>\n\n"
            "Теперь тебя ждут ежедневные литературные рекомендации от великих героев. "
            "Проверь завтра утром — и пусть каждое утро будет началом вдохновения."
        )
    else:
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
