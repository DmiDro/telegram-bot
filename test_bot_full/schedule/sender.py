from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from datetime import datetime
import time
import logging

from utils.gpt import generate_daily_recommendation
from db.write import get_subscribed_users
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def setup_scheduler(bot: Bot):
    logging.info("🟡 Настройка планировщика...")

    tz_istanbul = timezone("Europe/Istanbul")

    # Показываем текущее время для диагностики
    logging.info(f"🕰️ Системное UTC время: {datetime.utcnow()}")
    logging.info(f"🕰️ Локальное время (Europe/Istanbul): {datetime.now(tz_istanbul)}")
    logging.info(f"🕰️ time.time(): {time.time()}")

    scheduler = AsyncIOScheduler(timezone=tz_istanbul)

    @scheduler.scheduled_job(
        CronTrigger(hour=17, minute=50, timezone=tz_istanbul)  # Явно указываем таймзону!
    )
    async def send_recommendations():
        now = datetime.now(tz_istanbul).strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"📅 Планировщик сработал в {now} (Europe/Istanbul)")

        users = await get_subscribed_users()
        logging.info(f"👥 Пользователей для рассылки: {len(users)}")

        for user_id in users:
            try:
                logging.info(f"📤 Отправка пользователю: {user_id}")
                recommendation = await generate_daily_recommendation(user_id)

                keyboard = InlineKeyboardMarkup(inline_keyboard=[[ 
                    InlineKeyboardButton(text="👍", callback_data="feedback_like"),
                    InlineKeyboardButton(text="👎", callback_data="feedback_dislike"),
                ]])

                await bot.send_message(
                    user_id,
                    recommendation,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=keyboard
                )

                logging.info(f"✅ Успешно отправлено: {user_id}")

            except Exception as e:
                logging.warning(f"⚠️ Ошибка при отправке {user_id}: {e}")

    scheduler.start()
    logging.info("✅ Планировщик запущен (Europe/Istanbul)")
