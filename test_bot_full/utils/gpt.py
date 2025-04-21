import random
import logging
import httpx
from db import get_hero_list

# 🌐 URL FastAPI-прокси (порт 8000 должен быть доступен)
PROXY_URL = "http://45.155.102.141:8000/chat"

# 📦 HTTP-клиент
http_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))

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

Стиль: метафоричный, философский или художественный с юмором, с пожеланиями на день. Объём — 1–3 предложения, примерно 200 символов. Особенно делать акцент на свойства архетипа, соционики. Обращения должны быть без принадлежности к какому-либо гендеру. Обязательно упомянуть слово "результат", избегай тавтологии.
""".strip()

    try:
        logging.info(f"📤 [gpt] Отправка prompt через FastAPI-прокси для героя: {name}")
        response = await http_client.post(PROXY_URL, json={"prompt": prompt})
        response.raise_for_status()

        data = await response.json()  # ← исправлено

        advice = data.get("result") or data.get("message") or data
        if isinstance(advice, dict):
            advice = str(advice)

        advice = advice.strip()
        logging.info(f"🖍️ [gpt] Получен ответ от FastAPI-прокси:\n{advice}")

    except Exception as e:
        logging.error(f"❌ [gpt] Ошибка при обращении к прокси: {e}")
        advice = "Сегодняшний результат зависит от твоего взгляда на него. Делай выбор — он твой."
        logging.info("📎 [gpt] Использована заглушка по ошибке.")

    return (
        f"🕊 <b>Послание на сегодня:</b>\n\n"
        f"{advice}\n\n"
        f"С уважением, {signature_html}\n"
        f"<i>{description}</i>"
    )
