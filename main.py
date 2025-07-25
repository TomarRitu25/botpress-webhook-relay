from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.post("/")
async def webhook_relay(request: Request):
    data = await request.json()

    sender = data.get("sender")
    message = data.get("message")
    if not sender or not message:
        return {"error": "Missing 'sender' or 'message'"}

    bp_event = {
        "type": "custom",
        "name": "webhook",
        "payload": {
            "sender": sender,
            "message": message
        }
    }

    bot_id = "276bd220-e084-4ace-87e7-20b0bcf3b834"  # <-- Replace this with your real bot ID
    botpress_url = f"https://studio.botpress.cloud/v1/bots/{bot_id}/external/events"

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(botpress_url, json=bp_event)
            res.raise_for_status()
            return {"status": "forwarded", "botpress": res.json()}
        except Exception as e:
            return {"error": str(e)}
