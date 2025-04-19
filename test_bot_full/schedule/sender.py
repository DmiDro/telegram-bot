import logging
import time
from datetime import datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from utils.gpt import generate_daily_recommendation
from db.write import get_subscribed_users


def setup_scheduler(bot: Bot):
    logging.info("🟡 Настройка планировщика...")

    tz_istanbul = timezone("Europe/Istanbul")

    logging.info(f"🕰️ Системное UTC время: {datetime.utcnow()}")
    logging.info(f"🕰️ Локальное время (Europe/Istanbul): {datetime.now(tz_istanbul)}")
    logging.info(f"🕰️ time.time(): {time.time()}")

    scheduler = AsyncIOScheduler(timezone=tz_istanbul)

    async def send_recommendations():
        now = datetime.now(tz_istanbul).strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"📅 Планировщик сработал в {now} (Europe/Istanbul)")

        try:
            users = await get_subscribed_users()
            logging.info(f"👥 Пользователей для рассылки: {len(users)}")
        except Exception as e:
            logging.error(f"❌ Ошибка при получении пользователей: {e}")
            return


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

    try:
        scheduler.add_job(
            send_recommendations,
            CronTrigger(hour=2, minute=38, timezone=tz_istanbul),
            name="Ежедневная рассылка"
        )
        logging.info("📌 Задача send_recommendations добавлена в планировщик.")
    except Exception as e:
        logging.error(f"❌ Ошибка при добавлении задачи: {e}")

    scheduler.start()
    logging.info("✅ Планировщик успешно запущен.")
