from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BOTPRESS_WEBHOOK_URL = "https://webhook.botpress.cloud/68fae66c-1088-4960-877d-9e065bd72e72"  # Full webhook URL

@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        payload = await request.json()
        print("Received payload:", payload)

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

        webhook_payload = {
            "text": text,
            "userId": user_id
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(BOTPRESS_WEBHOOK_URL, json=webhook_payload)
            print("Botpress Webhook Response:", response.status_code, response.text)

        return {
            "status": "relayed",
            "botpress_status": response.status_code,
            "botpress_response": response.text
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": str(e)}

