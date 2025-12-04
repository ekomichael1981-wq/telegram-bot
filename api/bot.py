from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    try:
        update = await request.json()
        
        if "message" not in update:
            return JSONResponse({"ok": True})
        
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").lower()
        
        # Show typing indicator
        await send_action(chat_id, "typing")
        
        # Japa Genie - Immigration Assistant
        response = generate_immigration_response(text)
        
        # Send message back
        await send_telegram_message(chat_id, response)
        
        return JSONResponse({"ok": True})
        
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse({"ok": True})

def generate_immigration_response(text: str) -> str:
    """Generate responses for immigration queries"""
    
    # Commands
    if text == "/start":
        return """🧞‍♂️ *Welcome to Japa Genie!*
        
I'm your AI immigration assistant. I can help with:
• Visa requirements
• Work permits
• Study abroad
• Relocation tips
• Country-specific information

Try asking:
• "Canada visa requirements"
• "How to get UK work permit"
• "Study in Germany"
• "USA green card process"

Type /help for commands."""
    
    elif text == "/help":
        return """📋 *Available Commands:*
        
/start - Welcome message
/help - This help menu
/visa - General visa information
/work - Work permit guide
/study - Study abroad options
/countries - Popular destinations

Or ask questions like:
• "Canada PR process"
• "UK skilled worker visa"
• "Australia points system"
• "Germany job seeker visa" """
    
    elif text == "/visa":
        return """🛂 *Visa Information*
        
Common visa types:
1. *Tourist Visa* - Short visits
2. *Student Visa* - For education
3. *Work Visa* - Employment
4. *Business Visa* - Business activities
5. *Permanent Residence* - Long-term stay

Requirements usually include:
• Valid passport
• Application forms
• Passport photos
• Proof of funds
• Purpose documentation"""
    
    elif text == "/work":
        return """💼 *Work Permits*
        
Popular work visas:
• *Canada*: Express Entry, PNP
• *USA*: H-1B, L-1, O-1
• *UK*: Skilled Worker Visa
• *Germany*: EU Blue Card
• *Australia*: SkillSelect

Requirements:
• Job offer from employer
• Educational credentials
• Work experience
• Language proficiency
• Medical examination"""
    
    elif text == "/study":
        return """🎓 *Study Abroad*
        
Top study destinations:
• *USA*: F-1 visa, OPT program
• *Canada*: Study Permit, PGWP
• *UK*: Student visa, Graduate route
• *Australia*: Student visa, Temporary Graduate
• *Germany*: Free tuition in public universities

Requirements:
• University acceptance letter
• Proof of funds
• Language test (IELTS/TOEFL)
• Educational transcripts"""
    
    # Keyword-based responses
    elif any(word in text for word in ["canada", "canadian"]):
        return """🇨🇦 *Canada Immigration*
        
Popular programs:
1. *Express Entry* (FSW, FST, CEC)
2. *Provincial Nominee Program* (PNP)
3. *Atlantic Immigration Program*
4. *Startup Visa*
5. *Family Sponsorship*

Processing time: 6-8 months
Language: English/French (IELTS/TEF)
CRS score calculator available online"""
    
    elif any(word in text for word in ["usa", "america", "united states"]):
        return """🇺🇸 *USA Immigration*
        
Common pathways:
• *H-1B* - Specialty occupations
• *L-1* - Intra-company transfer
• *O-1* - Extraordinary ability
• *EB-2/EB-3* - Employment-based green cards
• *Diversity Visa Lottery*

Green Card process: 1-3 years
H-1B lottery: April each year"""
    
    elif any(word in text for word in ["uk", "britain", "united kingdom"]):
        return """🇬🇧 *UK Immigration*
        
Points-based system:
• *Skilled Worker Visa* - 70 points required
• *Health & Care Worker Visa*
• *Global Talent Visa*
• *Scale-up Visa*
• *Graduate Visa* (for UK graduates)

Salary threshold: £38,700+
English requirement: CEFR B1 level"""
    
    elif any(word in text for word in ["germany", "deutschland"]):
        return """🇩🇪 *Germany Immigration*
        
Options:
• *EU Blue Card* - University degree + job offer
• *Job Seeker Visa* - 6 months to find job
• *Freelancer Visa* - Self-employment
• *Student Visa* - Study then 18-month job seeker

Permanent Residence: 21-33 months
Language: German A1-B2 (depending on visa)"""
    
    elif any(word in text for word in ["australia", "aussie"]):
        return """🇦🇺 *Australia Immigration*
        
SkillSelect system:
• *Skilled Independent visa* (189)
• *Skilled Nominated visa* (190)
• *Skilled Work Regional visa* (491)
• *Employer Sponsored visas* (482, 186)

Points test: Minimum 65 points
Occupation lists: MLTSSL, STSOL, ROL"""
    
    # Default response for other questions
    else:
        return f"""🧞‍♂️ *Japa Genie Response*

You asked: "{text}"

I specialize in immigration and relocation advice. Try asking about:
• Specific countries (Canada, USA, UK, etc.)
• Visa types (work, study, tourist)
• Immigration processes
• Documentation requirements

Or use /help to see available commands."""

async def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })

async def send_action(chat_id: int, action: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "action": action
        })

@app.get("/")
async def health():
    return {"status": "healthy", "service": "japa-genie-bot"}

