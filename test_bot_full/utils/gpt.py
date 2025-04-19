import random
import logging
import os
import httpx
from openai import AsyncOpenAI
from db import get_hero_list

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROXY = os.getenv("OPENAI_PROXY")

print(">>> OPENAI_PROXY:", repr(OPENAI_PROXY))  # ✅ Вставка отладки

# Проверка наличия proxy и корректного формата
http_client = httpx.AsyncClient(proxies=OPENAI_PROXY) if OPENAI_PROXY else None

# Инициализация клиента
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    http_client=http_client
)


async def generate_daily_recommendation(user_id: str, archetype: str = "", maturity: str = "", socionics: str = "") -> str:
    logging.info(f"🚀 [gpt] Генерация послания для user_id: {user_id}")

    heroes = await get_hero_list()
    if not heroes:
        logging.warning("⚠️ [gpt] Персонажи не загружены из БД")
        return "⚠️ Персонажи не загружены. Попробуйте позже."

    logging.info(f"✅ [gpt] Загрузили {len(heroes)} героев из базы.")

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
""".strip()

    try:
        logging.info(f"📤 [gpt] Отправка prompt в OpenAI для героя: {name}")
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        advice = response.choices[0].message.content.strip()
        logging.info(f"🖍️ [gpt] Получен ответ от GPT:\n{advice}")
    except Exception as e:
        logging.error(f"❌ [gpt] Ошибка генерации рекомендации: {e}")
        advice = "Сегодняшний результат зависит от твоего взгляда на него. Делай выбор — он твой."
        logging.info("📎 [gpt] Использована заглушка по ошибке.")

    return (
        f"🕊 <b>Послание на сегодня:</b>\n\n"
        f"{advice}\n\n"
        f"С уважением, {signature_html}\n"
        f"<i>{description}</i>"
    )
