from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message
from test_bot_full.utils.keyboards import menu_keyboard, unsubscribe_confirmation_keyboard

router = Router()

# Команда /start
@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Готов пройти тест?", reply_markup=await menu_keyboard())

# Команда /tests
@router.message(Command("tests"))
async def list_tests(message: Message):
    await message.answer("Вот доступные тесты:", reply_markup=await menu_keyboard())

# Команда /unsubscribe (или текст "отписаться")
@router.message(F.text.lower() == "отписаться")
@router.message(F.text.startswith("/unsubscribe"))
async def unsubscribe_command(message: Message):
    await message.answer("Вы точно хотите отписаться от прогноза?", reply_markup=unsubscribe_confirmation_keyboard())
