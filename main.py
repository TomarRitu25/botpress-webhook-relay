from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BOTPRESS_API_URL = "https://bots.botpress.cloud/v1/chat/messages"
BOTPRESS_BOT_ID = os.getenv("BOTPRESS_BOT_ID")
BOTPRESS_CLIENT_TOKEN = os.getenv("BOTPRESS_CLIENT_TOKEN")  # From bot > Settings > API Key

@app.post("/webhook")
async def webhook_handler(request: Request):
    payload = await request.json()
    print("Received payload:", payload)

    # Extract user_id and text
    if "entry" in payload:
        try:
            message_obj = payload["entry"][0]["messaging"][0]
            user_id = message_obj["sender"]["id"]
            text = message_obj["message"]["text"]
        except (KeyError, IndexError, TypeError):
            return {"error": "Meta-style payload malformed"}
    elif "sender" in payload and "message" in payload:
        user_id = payload["sender"]
        text = payload["message"]
    else:
        return {"error": "Unexpected payload format"}

    botpress_payload = {
        "botId": BOTPRESS_BOT_ID,
        "channel": "web",
        "payload": {
            "text": text,
            "type": "text"
        },
        "user": {
            "id": user_id
        }
    }

    headers = {
        "Authorization": f"Bearer {BOTPRESS_CLIENT_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(BOTPRESS_API_URL, headers=headers, json=botpress_payload)

    return {"status": "relayed", "botpress_response": response.json()}

