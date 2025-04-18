import os
import random
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI
from db import get_hero_list  # 👈 список героев из БД

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logging.error("❌ OPENAI_API_KEY не найден в переменных окружения!")
else:
    logging.info("🔑 OPENAI_API_KEY загружен.")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def generate_daily_recommendation(user_id: str, archetype: str = "", maturity: str = "", socionics: str = "") -> str:
    logging.info(f"🚀 Генерация послания для user_id: {user_id}")
    
    heroes = await get_hero_list()
    if not heroes:
        logging.warning("⚠️ Персонажи не загружены из БД")
        return "⚠️ Персонажи не загружены. Попробуйте позже."

    logging.info(f"✅ Загрузили {len(heroes)} героев из базы.")

    char = random.choice(heroes)
    name = char["name"]
    description = char["description"]
    link = char.get("link", "")

    signature_html = f'<a href="{link}">{name}</a>' if link else name

    prompt = f"""
Ты — {name}. Твоя суть: {description}.
Ты даёшь короткую и вдохновляющую рекомендацию, как если бы ты был реальным человеком с таким характером.

Не упоминай слово "тест", "архетип", ID или цифры. Не обращайся по имени. Просто дай художественный совет.

Контекст:
Архетип: {archetype or "неизвестен"}
Эмоциональная зрелость: {maturity or "неизвестна"}
Соционика: {socionics or "неизвестна"}

Стиль: метафоричный, философский или художественный с юмором, с пожеланиями на день. Объём — 1–3 предложения, примерно 200 символов. Особенно делать акцент на свойства архетипа, соционики. Обращения должны быть без принадлежности к какому либо гендерному полу. Обязательно упомянуть слово "результат", избегай тавтологии.
"""

    try:
        logging.info(f"📤 Отправка prompt в OpenAI для героя: {name}")
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        logging.info("📦 Ответ от OpenAI получен")

        advice = response.choices[0].message.content.strip()
        logging.info(f"🖍️ Сгенерированное послание:\n{advice}")

        return (
            f"🕊 <b>Послание на сегодня:</b>\n\n"
            f"{advice}\n\n"
            f"С уважением, {signature_html}\n"
            f"<i>{description}</i>"
        )

    except Exception as e:
        logging.error(f"❌ Ошибка генерации рекомендации: {e}")
        return f"⚠️ Ошибка генерации рекомендации: {e}"
