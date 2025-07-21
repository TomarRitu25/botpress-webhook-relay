from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BOTPRESS_API_URL = "https://bots.botpress.cloud/v1/chat/messages"
BOTPRESS_BOT_ID = os.getenv("BOTPRESS_BOT_ID")
BOTPRESS_CLIENT_TOKEN = os.getenv("BOTPRESS_CLIENT_TOKEN")

@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        payload = await request.json()
        print("Received payload:", payload)

        # Meta-style payload (e.g. Facebook)
        if "entry" in payload:
            try:
                message_obj = payload["entry"][0]["messaging"][0]
                user_id = message_obj["sender"]["id"]
                text = message_obj["message"]["text"]
            except (KeyError, IndexError, TypeError):
                return {"error": "Malformed Meta payload"}

        # Simple JSON test
        elif "sender" in payload and "message" in payload:
            user_id = payload["sender"]
            text = payload["message"]

        else:
            return {"error": "Unexpected payload format"}

        # Format Botpress request
        botpress_payload = {
            "botId": BOTPRESS_BOT_ID,
            "userId": user_id,
            "payload": {
                "type": "text",
                "text": text
            }
        }

        headers = {
            "Authorization": f"Bearer {BOTPRESS_CLIENT_TOKEN}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            bp_response = await client.post(BOTPRESS_API_URL, headers=headers, json=botpress_payload)

        try:
            bp_response_data = bp_response.json()
        except Exception:
            bp_response_data = {"error": "Invalid JSON response from Botpress"}

        return {
            "status": "relayed",
            "botpress_status": bp_response.status_code,
            "botpress_response": bp_response_data
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/debug")
async def debug():
    return {"message": "Botpress relay is working!"}

