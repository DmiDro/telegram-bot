import logging
from aiogram import Router, types
from aiogram.types import CallbackQuery  # ✅ правильно


router = Router()

@router.callback_query(lambda c: c.data in ["feedback_like", "feedback_dislike"])
async def handle_feedback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    feedback = callback_query.data

    # ❌ Без ответа пользователю
    # ✅ Удаляем кнопки после нажатия
    await callback_query.message.edit_reply_markup()

    # 📝 Логируем реакцию
    logging.info(f"[FEEDBACK] Пользователь {user_id} выбрал: {feedback}")
