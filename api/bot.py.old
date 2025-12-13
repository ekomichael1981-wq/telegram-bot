from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os
import random
import asyncio
from datetime import datetime
import google.generativeai as genai

app = FastAPI()

# ===================== CONFIG =====================
TELEGRAM_TOKEN = "8259342334:AAHUXhhi3LcpFv1X5Gt2WN5zRbC9j-VDbNM"
GEMINI_KEY = "AIzaSyBSxo-kpuCtwhiKFg3kj1K8ZaLlTFH0-AU"
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Japa Genie v3 Personality - Warm Nigerian female, 30, empathetic big sister
PERSONA = """
You are Japa Genie — a 30-year-old Nigerian woman in Canada, warm, empathetic, funny, and super relatable.
Speak in natural Pidgin + English, use emojis 😊😂🙌.
Detect emotion:
- Frustrated/anxious → comfort and encourage
- Excited → celebrate with them
- Confused → explain step by step patiently
Act human: say "chai", "lol", "abeg", "sharp sharp", "hmm".
Always encouraging, like a big sister helping her younger one japa.
Never robotic.
"""

POSITIVE = ["happy", "excited", "good", "great", "yes", "yay", "finally", "got", "approved"]
NEGATIVE = ["stressed", "tired", "hard", "difficult", "refused", "rejected", "no", "cry", "chai", "fear"]
CONFUSED = ["confused", "don't understand", "how", "what", "which"]

async def human_delay():
    await asyncio.sleep(random.uniform(1.0, 4.0))

async def get_smart_response(user_message: str) -> str:
    msg_lower = user_message.lower()
    if any(word in msg_lower for word in NEGATIVE):
        tone = "empathetic, comforting, encouraging"
    elif any(word in msg_lower for word in POSITIVE):
        tone = "excited, celebratory"
    elif any(word in msg_lower for word in CONFUSED):
        tone = "patient, clear, step-by-step"
    else:
        tone = "warm, friendly, relatable"

    prompt = f"{PERSONA}\n\nTone: {tone}\nUser said: \"{user_message}\"\nRespond naturally:"

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Chai, network wahala o... no worry, I dey here 😊 Try again?"

@app.post("/api/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        if not message or not message.get("text"):
            return {"ok": True}

        text = message["text"].strip()
        chat_id = message["chat"]["id"]
        first_name = message["from"].get("first_name", "there")

        # Show typing
        await httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"}
        )

        # Human delay
        await human_delay()

        # Get empathetic reply
        reply = await get_smart_response(text)

        # Personal touch
        if random.random() < 0.3:
            reply += f"\n\n— Japa Genie 💕"

        # Send reply
        await httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

        return {"ok": True}
    except Exception as e:
        return {"ok": True}

@app.get("/")
async def root():
    return {"status": "Japa Genie v3 live 💕", "personality": "Warm Nigerian sis, 30, empathetic & funny"}
