# test_bot_full/handlers/commands.py

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message
from utils.keyboards import menu_keyboard, unsubscribe_confirmation_keyboard

router = Router()

# Команда /unsubscribe (или текст "отписаться")
@router.message(F.text.lower() == "отписаться")
@router.message(F.text.startswith("/unsubscribe"))
async def unsubscribe_command(message: Message):
    await message.answer("Вы точно хотите отписаться от прогноза?", reply_markup=unsubscribe_confirmation_keyboard())
