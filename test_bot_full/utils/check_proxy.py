import asyncio
import os
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROXY = os.getenv("OPENAI_PROXY", "").strip()

if OPENAI_PROXY.startswith("socks5h://"):
    OPENAI_PROXY = "socks5://" + OPENAI_PROXY[len("socks5h://"):]

print(">>> OPENAI_PROXY:", repr(OPENAI_PROXY))

async def test_proxy():
    try:
        async with httpx.AsyncClient(proxies={"all://": OPENAI_PROXY}) as client:
            r = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
            )
            print("✅ Прокси работает:", r.status_code)
            print("Ответ:", r.text)
    except Exception as e:
        print("❌ Ошибка подключения через прокси:", e)

if __name__ == "__main__":
    asyncio.run(test_proxy())
