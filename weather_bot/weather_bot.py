import os
import requests
import logging
import asyncio
from random import choice
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# Загружаем переменные окружения
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TELEGRAM_BOT_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Ошибка! Проверь .env файл, отсутствует TELEGRAM_BOT_TOKEN или WEATHER_API_KEY!")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

CITY_NAME = "Заянье"
LAT = 58.779
LON = 28.626

# --- Погода ---
def get_weather(hours_ahead=0):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={LAT},{LON}&hours=24&lang=ru"
    try:
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            return "Ошибка! Не удалось получить погоду."

        current = data["current"]
        forecast = data["forecast"]["forecastday"][0]["hour"]

        if hours_ahead == 0:
            selected_weather = current
            time_label = "Сейчас"
        else:
            selected_weather = next((h for h in forecast if h["time"].endswith(f"{hours_ahead:02d}:00")), current)
            time_label = f"Через {hours_ahead} часов" if hours_ahead != 24 else "Завтра"

        temp = selected_weather["temp_c"]
        condition = selected_weather["condition"]["text"]
        wind_speed = selected_weather["wind_kph"]
        humidity = selected_weather["humidity"]

        return (
            f"\U0001F324 Погода в <b>{CITY_NAME}</b>\n"
            f"\U0001F552 Время: <b>{time_label}</b>\n"
            f"\U0001F321 Температура: <b>{temp}°C</b>\n"
            f"\U0001F4A8 Ветер: <b>{wind_speed} км/ч</b>\n"
            f"\U0001F4A7 Влажность: <b>{humidity}%</b>\n"
            f"\U0001F30D Состояние: <b>{condition}</b>"
        )
    except Exception as e:
        return f"⚠ Ошибка получения погоды: {e}"

# --- Клавиатуры ---
def main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton(text="\U0001F324 Погода", callback_data="weather_menu")],
        [InlineKeyboardButton(text="\U0001F3AE Камень-Ножницы-Бумага", callback_data="rps_game")],
        [InlineKeyboardButton(text="\U0001F4CD Отправить координаты", callback_data="send_location")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def weather_keyboard():
    buttons = [
        [InlineKeyboardButton(text="\U0001F324 Сейчас", callback_data="weather_now")],
        [InlineKeyboardButton(text="⏳ Через 6 часов", callback_data="weather_6h")],
        [InlineKeyboardButton(text="\U0001F319 Ночью", callback_data="weather_night")],
        [InlineKeyboardButton(text="☀ Завтра", callback_data="weather_tomorrow")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Команды и обработчики ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("👋 Привет! Выберите действие:", reply_markup=main_menu_keyboard())

@dp.callback_query()
async def handle_callbacks(callback_query: types.CallbackQuery):
    data = callback_query.data

    if data == "weather_menu":
        await callback_query.message.edit_text("\U0001F324 Выберите время:", reply_markup=weather_keyboard())

    elif data.startswith("weather_"):
        hours = {"weather_now": 0, "weather_6h": 6, "weather_night": 22, "weather_tomorrow": 24}.get(data, 0)
        weather_info = get_weather(hours)
        await callback_query.message.edit_text(weather_info, reply_markup=weather_keyboard())

    elif data == "rps_game":
        rps_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🪨 Камень", callback_data="rps_rock")],
            [InlineKeyboardButton(text="✂️ Ножницы", callback_data="rps_scissors")],
            [InlineKeyboardButton(text="📄 Бумага", callback_data="rps_paper")],
        ])
        await callback_query.message.edit_text("Выберите жест:", reply_markup=rps_keyboard)

    elif data.startswith("rps_"):
        options = {
            "rps_rock": "🪨 Камень",
            "rps_scissors": "✂️ Ножницы",
            "rps_paper": "📄 Бумага",
        }
        user_choice = options[data]
        bot_choice_key = choice(list(options.keys()))
        bot_choice = options[bot_choice_key]

        result = determine_rps_result(data, bot_choice_key)
        await callback_query.message.edit_text(
            f"Вы: {user_choice}\nБот: {bot_choice}\n\n<b>{result}</b>",
            reply_markup=main_menu_keyboard()
        )

    elif data == "send_location":
        await callback_query.message.answer_location(latitude=LAT, longitude=LON)

# --- Логика игры ---
def determine_rps_result(user, bot):
    if user == bot:
        return "Ничья!"
    wins = {
        "rps_rock": "rps_scissors",
        "rps_scissors": "rps_paper",
        "rps_paper": "rps_rock"
    }
    return "Вы выиграли! 🎉" if wins[user] == bot else "Вы проиграли 😢"

# --- Запуск ---
async def main():
    logging.info("✅ Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
