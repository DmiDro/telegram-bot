import os
import requests
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# Загружаем переменные окружения
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен бота
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # API-ключ погоды

# Проверяем, что токены есть
if not TELEGRAM_BOT_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Ошибка! Проверь .env файл, отсутствует TELEGRAM_BOT_TOKEN или WEATHER_API_KEY!")

# Логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# 📍 Локация Заянье
CITY_NAME = "Заянье"
LAT = 55.789  # Примерная широта
LON = 49.122  # Примерная долгота

# Функция для получения погоды
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

        # Формируем текст ответа
        temp = selected_weather["temp_c"]
        condition = selected_weather["condition"]["text"]
        wind_speed = selected_weather["wind_kph"]
        humidity = selected_weather["humidity"]

        return (
            f"🌤 Погода в <b>{CITY_NAME}</b>\n"
            f"🕒 Время: <b>{time_label}</b>\n"
            f"🌡 Температура: <b>{temp}°C</b>\n"
            f"💨 Ветер: <b>{wind_speed} км/ч</b>\n"
            f"💧 Влажность: <b>{humidity}%</b>\n"
            f"🌍 Состояние: <b>{condition}</b>"
        )
    except Exception as e:
        return f"⚠ Ошибка получения погоды: {e}"

# Клавиатура с кнопками
def weather_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🌤 Сейчас", callback_data="weather_now")],
        [InlineKeyboardButton(text="⏳ Через 6 часов", callback_data="weather_6h")],
        [InlineKeyboardButton(text="🌙 Ночью", callback_data="weather_night")],
        [InlineKeyboardButton(text="☀ Завтра", callback_data="weather_tomorrow")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Команда /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("☀ Привет! Я бот, показывающий погоду в Заянье.\nВыберите время:", reply_markup=weather_keyboard())

# Обработчик кнопок
@dp.callback_query()
async def handle_weather_buttons(callback_query: types.CallbackQuery):
    if callback_query.data == "weather_now":
        weather_info = get_weather(0)
    elif callback_query.data == "weather_6h":
        weather_info = get_weather(6)
    elif callback_query.data == "weather_night":
        weather_info = get_weather(22)
    elif callback_query.data == "weather_tomorrow":
        weather_info = get_weather(24)
    else:
        weather_info = "⚠ Ошибка! Выберите одну из кнопок."

    await callback_query.message.edit_text(weather_info, reply_markup=weather_keyboard())

# Запуск бота
async def main():
    logging.info("✅ Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
