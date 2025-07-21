from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Botpress API details from environment
BOTPRESS_API_URL = "https://bots.botpress.cloud/v1/chat/messages"
BOTPRESS_BOT_ID = os.getenv("BOTPRESS_BOT_ID")
BOTPRESS_CLIENT_TOKEN = os.getenv("BOTPRESS_CLIENT_TOKEN")  # From Botpress > Settings > API Key

@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        payload = await request.json()
        print("Received payload:", payload)

        # Handle Meta-style payload
        if "entry" in payload:
            try:
                message_obj = payload["entry"][0]["messaging"][0]
                user_id = message_obj["sender"]["id"]
                text = message_obj["message"]["text"]
            except (KeyError, IndexError, TypeError):
                return {"error": "Meta-style payload malformed"}

        # Handle simple payload
        elif "sender" in payload and "message" in payload:
            user_id = payload["sender"]
            text = payload["message"]

        else:
            return {"error": "Unexpected payload format"}

        # Prepare Botpress payload
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

        # Send message to Botpress
        async with httpx.AsyncClient() as client:
            bp_response = await client.post(BOTPRESS_API_URL, headers=headers, json=botpress_payload)
            response_text = bp_response.text
            print("Botpress response:", bp_response.status_code, response_text)

            try:
                response_json = bp_response.json()
            except Exception as e:
                print("Error parsing JSON response from Botpress:", str(e))
                response_json = {"error": "Invalid JSON response from Botpress"}

        return {
            "status": "relayed",
            "botpress_status": bp_response.status_code,
            "botpress_response": response_json
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": str(e)}

# Optional browser test route
@app.get("/debug")
async def debug():
    return {"message": "Botpress relay server is running!"}

