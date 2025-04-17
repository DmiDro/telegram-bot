# 📁 schedule/sender.py

import os
import logging
import datetime
from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.gpt import generate_daily_recommendation
from db.write import get_subscribed_users


def setup_scheduler(bot: Bot):
    logging.info("🟡 Настройка планировщика...")

    # Создаём планировщик с часовым поясом Москвы
    scheduler = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))

    @scheduler.scheduled_job(CronTrigger(hour=11, minute=41))
    async def send_recommendations():
        now = datetime.datetime.now(timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"🚀 ЗАДАНИЕ ВЫПОЛНЕНО! Время (МСК): {now}")

        users = await get_subscribed_users()
        logging.info(f"👥 Подписчиков: {len(users)}")

        for user_id in users:
            try:
                logging.info(f"📤 Отправка пользователю: {user_id}")
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

                logging.info(f"✅ Успешно отправлено: {user_id}")

            except Exception as e:
                logging.warning(f"⚠️ Ошибка при отправке {user_id}: {e}")

    scheduler.start()
    logging.info("✅ Планировщик запущен (МСК 11:41)")
