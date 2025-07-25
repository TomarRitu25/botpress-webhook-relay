from fastapi import FastAPI, Request
import httpx

app = FastAPI()

BOTPRESS_WEBHOOK = "https://webhook.botpress.cloud/2b379b7d-0abf-4f6d-aa36-a4408e7bd16c"

@app.post("/")
async def handle_webhook(request: Request):
    payload = await request.json()

    # Instagram format
    if "entry" in payload:
        for entry in payload["entry"]:
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                message_text = messaging_event.get("message", {}).get("text", "")

                # Forward to Botpress
                await httpx.post(
                    BOTPRESS_WEBHOOK,
                    json={
                        "type": "text",
                        "text": message_text,
                        "from": sender_id
                    }
                )
    return {"status": "ok"}

