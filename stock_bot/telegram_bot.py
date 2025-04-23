import os
import httpx
from fastapi import FastAPI, Request
from pydantic import BaseModel

# Настройки
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SOCKS5_PROXY = "socks5://proxyuser:supersecretpass@127.0.0.1:8389"
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-3.5-turbo"

app = FastAPI()

# Структура входящего запроса
class PromptRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(request: PromptRequest):
    try:
        async with httpx.AsyncClient(proxies=SOCKS5_PROXY, timeout=20.0) as client:
            response = await client.post(
                OPENAI_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": request.prompt}],
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            return {"result": reply.strip()}
    except Exception as e:
        return {"error": str(e)}
