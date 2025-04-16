import logging
from aiogram import Router, types
from aiogram.filters import Command

from utils.keyboards import menu_keyboard
from db.write import get_completed_tests  # ✅ доступ к БД

router = Router()

# Храним последнее меню (user_id -> message_id)
user_menu_messages = {}

# ✅ Проверка: это первый запуск пользователя или нет
async def is_first_launch(user_id: int) -> bool:
    completed = await get_completed_tests(user_id)
    return len(completed) == 0

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    logging.info(f"[START] Команда /start от user_id: {user_id}")

    try:
        first_launch = await is_first_launch(user_id)
        logging.info(f"[START] Первый запуск: {first_launch}")

        # Удаляем сообщение /start
        try:
            await message.delete()
        except Exception as e:
            logging.warning(f"[START] Не удалось удалить /start сообщение: {e}")

        # Текст приветствия
        if first_launch:
            text = """<b>Слова — это след.</b>
У каждого следа есть направление.
     Просто отзовись на то, что тебе близко.
Здесь нет правильного и неправильного —
только искреннее.
     А потом — герои книг и великие писатели.
Те, кто знали одиночество, восторг, страх и надежду.
Они заговорят так, словно знали тебя всегда."""
        else:
            text = "Привет! Готов пройти тест?"

        keyboard = await menu_keyboard(user_id)

        # Удаляем предыдущее меню, если было
        if user_id in user_menu_messages:
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=user_menu_messages[user_id]
                )
                logging.info(f"[START] Удалено старое меню у пользователя {user_id}")
            except Exception as e:
                logging.warning(f"[START] Не удалось удалить старое меню: {e}")

        # Отправляем новое меню
        sent = await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        user_menu_messages[user_id] = sent.message_id
        logging.info(f"[START] Отправлено новое меню пользователю {user_id}")

    except Exception as e:
        logging.error(f"[START] Ошибка в обработке /start: {e}")
        await message.answer("⚠️ Что-то пошло не так...")
