import random
import logging
from db import get_hero_list  # 👈 список героев из БД

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

    # 📌 Заглушка без вызова OpenAI
    advice = "Сегодняшний результат зависит от твоего взгляда на него. Делай выбор — он твой."

    logging.info("🖍️ [gpt] Сгенерированная заглушка успешно собрана.")

    return (
        f"🕊 <b>Послание на сегодня:</b>\n\n"
        f"{advice}\n\n"
        f"С уважением, {signature_html}\n"
        f"<i>{description}</i>"
    )
