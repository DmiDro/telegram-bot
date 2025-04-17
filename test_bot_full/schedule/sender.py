from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from datetime import datetime, timedelta
import logging

from utils.gpt import generate_daily_recommendation
from db.write import get_subscribed_users
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def setup_scheduler(bot: Bot):
    logging.info("🟡 Настройка планировщика...")

    scheduler = AsyncIOScheduler(timezone=timezone("Europe/Istanbul"))

    # 🕰 Основная ежедневная задача (например, в 09:01 по Стамбулу)
    @scheduler.scheduled_job(CronTrigger(hour=13, minute=25))
    async def send_recommendations():
        now = datetime.now(timezone("Europe/Istanbul")).strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"🚀 ЗАДАНИЕ ВЫПОЛНЯЕТСЯ! Время (Стамбул): {now}")

        users = await get_subscribed_users()
        logging.info(f"👥 Найдено пользователей для рассылки: {len(users)}")

        for user_id in users:
            try:
                logging.info(f"📤 Отправляем послание пользователю: {user_id}")
                recommendation = await generate_daily_recommendation(user_id)

                keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="👍", callback_data="feedback_like"),
                    InlineKeyboardButton(text="👎", callback_data="feedback_dislike")
                ]])

                await bot.send_message(
                    user_id,
                    recommendation,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=keyboard
                )

                logging.info(f"✅ Успешно отправлено пользователю {user_id}")

            except Exception as e:
                logging.warning(f"⚠️ Не удалось отправить пользователю {user_id}: {e}")

    # 🧪 Тестовая задача (один раз через 1 минуту после запуска)
    @scheduler.scheduled_job(
        "date",
        run_date=datetime.now(timezone("Europe/Istanbul")) + timedelta(minutes=1)
    )
    async def test_job():
        now = datetime.now(timezone("Europe/Istanbul")).strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"🧪 Тестовая задача выполнена в {now}! Планировщик работает.")

    scheduler.start()
    logging.info("✅ Планировщик запущен (Europe/Istanbul)")
