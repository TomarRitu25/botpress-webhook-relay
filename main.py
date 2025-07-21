from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
BOTPRESS_WEBHOOK_URL = os.getenv("BOTPRESS_WEBHOOK_URL")

@app.post("/webhook")
async def webhook_handler(request: Request):
    payload = await request.json()
    print("Received payload:", payload)

    # Extract message (for Meta-style payloads)
    try:
        entry = payload["entry"][0]
        message_obj = entry["messaging"][0]
        user_id = message_obj["sender"]["id"]
        text = message_obj["message"]["text"]
    except KeyError:
        return {"error": "Unexpected payload format"}

    relay_payload = {
        "sender": user_id,
        "message": text
    }

    async with httpx.AsyncClient() as client:
        await client.post(BOTPRESS_WEBHOOK_URL, json=relay_payload)

    return {"status": "relayed"}

