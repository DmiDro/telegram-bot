from aiogram import Router, types
from aiogram.filters import Command
from test_bot_full.utils.keyboards import menu_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выберите тест:", reply_markup=await menu_keyboard())

