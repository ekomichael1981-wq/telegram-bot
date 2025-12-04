from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI()

# Get your bot token from environment variable
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        
        if "message" not in update:
            return JSONResponse({"ok": True})
        
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        # Simple response - you can customize this later
        if text.startswith("/start"):
            response = "Hello! I'm your Telegram bot. How can I help you?"
        elif text.startswith("/help"):
            response = "I'm a simple echo bot. Just send me any message!"
        else:
            response = f"You said: {text}"
        
        # Send message back to user
        await send_telegram_message(chat_id, response)
        
        return JSONResponse({"ok": True})
        
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse({"ok": True})

async def send_telegram_message(chat_id: int, text: str):
    """Send a message through Telegram Bot API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })

@app.get("/")
async def health():
    return {"status": "healthy", "service": "telegram-bot"}

@app.get("/test")
async def test():
    return {"message": "Bot is working!"}
