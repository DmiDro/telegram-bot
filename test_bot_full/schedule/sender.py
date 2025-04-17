from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone  # <== обязательно

from utils.gpt import generate_daily_recommendation
from db.write import get_subscribed_users
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

def setup_scheduler(bot: Bot):
    logging.info("🟡 Настройка планировщика...")

    scheduler = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))  # 🕘 Москва

    @scheduler.scheduled_job(
        CronTrigger(hour=10, minute=45)  # 10:45 по Москве
    )
    async def send_recommendations():
        users = await get_subscribed_users()

        for user_id in users:
            try:
                recommendation = await generate_daily_recommendation(user_id)

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="👍", callback_data="feedback_like"),
                        InlineKeyboardButton(text="👎", callback_data="feedback_dislike"),
                    ]
                ])

                await bot.send_message(
                    user_id,
                    recommendation,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=keyboard
                )

                logging.info(f"✅ Отправлено пользователю {user_id}")

            except Exception as e:
                logging.warning(f"⚠️ Не удалось отправить {user_id}: {e}")

    scheduler.start()
    logging.info("✅ Планировщик запущен (МСК 09:08)")
