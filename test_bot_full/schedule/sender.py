from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.gpt import generate_daily_recommendation
from db.write import get_subscribed_users  # если ты хранишь функцию тут
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()

    @scheduler.scheduled_job("cron", hour=9, minute=8)
    async def send_recommendations():
        users = await get_subscribed_users()

        for user_id in users:
            try:
                recommendation = await generate_daily_recommendation(user_id)

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="👍", callback_data="feedback_like"),
                        InlineKeyboardButton(text="👎", callback_data="feedback_dislike"),
                    ],
                    # [InlineKeyboardButton(text="📤 Поделиться", switch_inline_query="Послание на день")]
                ])

                await bot.send_message(
                    user_id,
                    recommendation,
                    parse_mode="HTML",
                    disable_web_page_preview=True, # True False
                    reply_markup=keyboard
                )

                logging.info(f"Отправлено пользователю {user_id}")

            except Exception as e:
                logging.warning(f"Не удалось отправить {user_id}: {e}")

    scheduler.start()
