from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.write import update_subscription_status

router = Router()

# Обработчик команды/кнопки "отписаться"
@router.callback_query(F.data == "unsubscribe")
async def confirm_unsubscribe(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, отписаться", callback_data="confirm_unsubscribe"),
            InlineKeyboardButton(text="❌ Нет, оставить", callback_data="cancel_unsubscribe")
        ]
    ])
    await callback.message.answer(
        "Вы уверены, что хотите отписаться от ежедневных прогнозов?",
        reply_markup=markup
    )

# Подтверждение отписки
@router.callback_query(F.data == "confirm_unsubscribe")
async def do_unsubscribe(callback: types.CallbackQuery):
    await update_subscription_status(user_id=callback.from_user.id, status="NO")
    await callback.message.edit_text("Вы отписались от прогноза. Если передумаете — вернуться всегда можно.")

# Отмена отписки
@router.callback_query(F.data == "cancel_unsubscribe")
async def cancel_unsubscribe(callback: types.CallbackQuery):
    await callback.message.edit_text("Окей, вы остались с нами.")
