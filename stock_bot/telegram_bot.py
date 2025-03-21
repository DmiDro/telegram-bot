import os
from dotenv import load_dotenv  # ✅ Импортируем dotenv
import openai
import logging
import asyncio
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from xgboost import XGBRegressor  # ✅ Добавляем импорт XGBRegressor

# ✅ Загружаем переменные окружения
load_dotenv()
api_key = os.getenv("API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = 522869453  # 🔹 Укажи ID чата для уведомлений

# Логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=telegram_token, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Список популярных активов
popular_tickers = popular_tickers = {
    "AAPL": "🍏 Apple",
    "AMZN": "📦 Amazon",
    "GOOGL": "🌍 Google",
    "MSFT": "💻 Microsoft",
    "META": "📱 Meta",
    "NVDA": "🎮 Nvidia",
    "PG": "🏠 P&G",
}

async def safe_request(func, *args, retries=3, **kwargs):
    """Повторяет запрос к Telegram API при ошибках сети"""
    for _ in range(retries):
        try:
            return await func(*args, **kwargs)
        except aiohttp.ClientConnectionError:
            logging.warning("Ошибка сети, повторная попытка...")
            await asyncio.sleep(3)
    return None

async def get_stock_price(ticker):
    """Получаем текущую цену акций через Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        price_data = stock.history(period="1d")

        if price_data.empty:
            return f"❌ Ошибка: Данные по {ticker} не найдены!"

        return round(price_data["Close"].iloc[-1], 2)

    except Exception as e:
        return f"⚠ Ошибка получения данных: {e}"

async def plot_stock_chart(ticker):
    """Строим график цены акций за последние 6 месяцев"""
    stock = yf.Ticker(ticker)
    data = stock.history(period="6mo")

    if data.empty:
        return None

    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data["Close"], label=f"{ticker} Цена закрытия", color="blue")
    plt.xlabel("Дата")
    plt.ylabel("Цена (USD)")
    plt.title(f"График цен {ticker}")
    plt.legend()
    plt.grid()

    # Сохраняем в файл
    filename = f"{ticker}_chart.png"
    plt.savefig(filename, format="png")
    plt.close()

    return filename

async def train_xgboost_model(ticker):
    """Обучаем XGBoost для предсказания цен"""
    stock = yf.Ticker(ticker)
    data = stock.history(period="1y")

    if data.empty:
        return f"❌ Нет данных для {ticker}!"

    # Подготовка данных
    data["Return"] = data["Close"].pct_change().fillna(0)
    X = np.array(range(len(data))).reshape(-1, 1)
    y = data["Close"].values

    # Обучаем модель
    model = XGBRegressor(n_estimators=100, learning_rate=0.1)
    model.fit(X, y)

    return model

async def predict_xgboost_price(ticker, days=30):
    """Прогнозируем цену на 30 дней вперёд с XGBoost"""
    model = await train_xgboost_model(ticker)

    if isinstance(model, str):  # Если вернулась ошибка
        return model

    future_days = np.array(range(len(model.feature_importances_), len(model.feature_importances_) + days)).reshape(-1, 1)
    predictions = model.predict(future_days)

    return round(predictions[-1], 2)

async def analyze_stock(ticker):
    """Запрашиваем у GPT-4 анализ текущей цены акций"""
    price = await get_stock_price(ticker)

    if isinstance(price, str) and "Ошибка" in price:
        return price

    client = openai.OpenAI(api_key=api_key)
    prompt = f"Цена акций {ticker} сейчас ${price}. Какие факторы могут повлиять на рост или падение акций?"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def get_stock_buttons():
    """Создаём клавиатуру с кнопками и логотипами"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=ticker)]
            for ticker, name in popular_tickers.items()
        ]
    )
    return keyboard


@dp.message(Command("start"))
async def start_command(message: Message):
    await safe_request(message.answer, "📊 Выберите актив или введите тикер:", reply_markup=get_stock_buttons())

@dp.callback_query()
async def handle_button_click(callback_query: types.CallbackQuery):
    ticker = callback_query.data
    await safe_request(callback_query.message.answer, f"📊 Вы выбрали {ticker}")
    await send_stock_analysis(callback_query.message, ticker)

@dp.message()
async def send_stock_analysis(message: Message, ticker=None):
    """Отправляем цену, анализ, прогноз и график"""
    if not ticker:
        ticker = message.text.upper().strip()

    price = await get_stock_price(ticker)
    if isinstance(price, str) and "Ошибка" in price:
        await safe_request(message.answer, price)
        return

    analysis = await analyze_stock(ticker)
    prediction = await predict_xgboost_price(ticker, days=30)
    chart = await plot_stock_chart(ticker)

    await safe_request(
        message.answer,
        f"📊 <b>{ticker}</b>\n📈 Цена: <b>${price}</b>\n\n🧐 Анализ:\n{analysis}\n\n🔮 Прогноз XGBoost: ${prediction}"
    )

    if chart:
        chart_file = FSInputFile(chart)
        await safe_request(message.answer_photo, chart_file)

scheduler = AsyncIOScheduler()

async def check_price_changes():
    """Проверяем изменения цен и отправляем уведомления"""
    for ticker in popular_tickers:
        price_now = await get_stock_price(ticker)
        if isinstance(price_now, str):
            continue

        stock = yf.Ticker(ticker)
        price_old = stock.history(period="5d")["Close"].iloc[-2]

        change = ((price_now - price_old) / price_old) * 100
        if abs(change) > 5:
            msg = f"⚠ <b>{ticker}</b> изменилась на {round(change, 2)}%\n📈 Текущая цена: ${price_now}"
            await safe_request(bot.send_message, chat_id=123456789, text=msg)

scheduler.add_job(check_price_changes, "interval", minutes=30)

async def main():
    logging.info("✅ Бот запущен!")
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
