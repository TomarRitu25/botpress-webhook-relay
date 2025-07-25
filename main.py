from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

# Replace this with your actual Botpress webhook URL
BOTPRESS_WEBHOOK_URL = "https://studio.botpress.cloud/webhooks/276bd220-e084-4ace-87e7-20b0bcfb3b34/webhook"

@app.post("/")
async def relay_to_botpress(request: Request):
    try:
        data = await request.json()

        # Construct Botpress-compatible payload
        forward_payload = {
            "type": "custom",
            "channel": "webhook",
            "event": "webhook",
            "payload": {
                "sender": data.get("sender", "unknown"),
                "message": data.get("message", "")
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(BOTPRESS_WEBHOOK_URL, json=forward_payload)
            response.raise_for_status()

        return {"status": "forwarded", "botpress_response_code": response.status_code}
    
    except Exception as e:
        return {"status": "error", "details": str(e)}

