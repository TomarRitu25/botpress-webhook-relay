from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BOTPRESS_WEBHOOK_URL = os.getenv("BOTPRESS_WEBHOOK_URL")

@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        payload = await request.json()
        print("Received payload:", payload)

        if "entry" in payload:
            message_obj = payload["entry"][0]["messaging"][0]
            user_id = message_obj["sender"]["id"]
            text = message_obj["message"]["text"]
        elif "sender" in payload and "message" in payload:
            user_id = payload["sender"]
            text = payload["message"]
        else:
            return {"error": "Unexpected payload format"}

        # Forward to Botpress Webhook
        relay_payload = {
            "sender": user_id,
            "message": text
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(BOTPRESS_WEBHOOK_URL, json=relay_payload)
            print("Botpress Webhook Response:", response.status_code, response.text)

        return {
            "status": "relayed",
            "botpress_status": response.status_code,
            "botpress_response": response.text
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": str(e)}

@app.get("/debug")
async def debug():
    return {"message": "Webhook relay server is live"}

