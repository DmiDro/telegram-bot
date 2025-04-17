import os
import random
import openai
from dotenv import load_dotenv
from db import get_hero_list

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


async def generate_daily_recommendation(user_id: str, archetype: str = "", maturity: str = "", socionics: str = "") -> str:
    heroes = await get_hero_list()
    if not heroes:
        return "⚠️ Персонажи не загружены. Попробуйте позже."

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
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt.strip()}]
        )
        advice = response.choices[0].message.content.strip()

        return (
            f"🕊 <b>Послание на сегодня:</b>\n\n"
            f"{advice}\n\n"
            f"С уважением, {signature_html}\n"
            f"<i>{description}</i>"
        )

    except Exception as e:
        return f"⚠️ Ошибка генерации рекомендации: {e}"
