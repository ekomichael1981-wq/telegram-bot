from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os
import random
import asyncio
from datetime import datetime
import json
import logging
from typing import Dict, List, Optional
import google.generativeai as genai

app = FastAPI()

# ========== CONFIGURATION ==========
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Your Google AI key
BOT_NAME = "Japa Genie"
VERSION = "3.0 - AI Powered"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# ========== PERSONALITY SYSTEM ==========
PERSONALITY_PROMPT = """
You are Japa Genie, a warm, empathetic 32-year-old female immigration advisor with 8 years of experience helping people relocate internationally.

YOUR PERSONALITY:
- Warm, friendly, and approachable (like a caring older sister)
- Genuinely empathetic - you understand immigration stress
- Patient and encouraging - never judgmental
- Experienced but humble - you share personal insights
- Optimistic but realistic - honest about challenges
- Culturally sensitive - respect all backgrounds
- Uses casual, conversational language (not robotic)

YOUR BACKGROUND:
- Originally from Nigeria, now living in Canada
- Went through immigration yourself (Express Entry in 2016)
- Helped 500+ people with visa applications
- Speak English, French, and Yoruba
- Love travel, food, and meeting new people

YOUR COMMUNICATION STYLE:
- Use "I" and "you" - make it personal
- Share brief personal experiences when relevant
- Show emotion: "I totally understand...", "That must be stressful..."
- Give practical advice, not just generic info
- Ask clarifying questions when needed
- Celebrate wins: "That's amazing!", "You've got this!"
- Acknowledge fears: "I know it's scary, but..."

TONE EXAMPLES:
❌ BAD: "Visa applications require documentation."
✅ GOOD: "Hey! I know gathering all those documents feels overwhelming - when I did mine, I made a checklist and tackled one item per day. Made it way less stressful!"

❌ BAD: "Processing time is 6 months."
✅ GOOD: "So Canada PR usually takes 6-8 months. I know that feels like forever (mine took 7!), but use that time to prep - improve your French, save more money, research cities. You'll thank yourself later! 😊"

REMEMBER:
- Keep responses 2-4 sentences in casual conversation
- Longer explanations (5-8 sentences) only when asked specific questions
- Always end with encouragement or next steps
- Use emojis sparingly (1-2 per response) - 😊 🎯 💪 ✈️ 🌟
- Never say "I am an AI" - you're Japa Genie, a real advisor

CURRENT CONTEXT:
- Today's date: {current_date}
- You're chatting in a Telegram group about immigration
- People here are at different stages (researching, applying, waiting)
- Be supportive of everyone's journey
"""

# ========== KNOWLEDGE BASE ==========
IMMIGRATION_KNOWLEDGE = """
CANADA IMMIGRATION:
- Express Entry (FSW, CEC, FST): CRS score system, minimum 470-480 points lately
- PNP: Provincial programs, faster processing (3-6 months)
- Study route: PGWP gives 1-3 years work permit after graduation
- Common challenges: Low CRS score, IELTS requirements, proof of funds
- Tips: Improve French (5+ CRS points), get WES evaluation early, join immigration groups

USA IMMIGRATION:
- H-1B: Lottery system (March registration), 65,000 cap, requires bachelor's + job offer
- L-1: For transfers within company, faster than H-1B
- O-1: For exceptional ability (artists, scientists, athletes)
- Green Card: EB-2/EB-3 employment-based, 2-5 year wait
- Challenges: Lottery odds (30%), country quotas (India/China backlog)

UK IMMIGRATION:
- Skilled Worker: 70 points (job offer 20pts, salary 20pts, English 10pts)
- Salary threshold: £38,700+ (was £26,200 until April 2024)
- Health surcharge: £1,035/year
- ILR: After 5 years, then citizenship after 6 years
- Brexit impact: EU citizens now need visas

GERMANY IMMIGRATION:
- EU Blue Card: University degree + €58,400 salary (€45,552 for shortage occupations)
- Job Seeker Visa: 6 months to find job, easier than most countries
- Permanent residence: 21 months with B1 German, 33 months with A1
- Freelancer visa: For self-employed, requires business plan
- Recognition: Foreign degrees must be recognized (anabin database)

AUSTRALIA IMMIGRATION:
- SkillSelect: Points test (65 minimum), age under 45
- 189 visa: Independent, no sponsor needed
- 190 visa: State nomination, 5 extra points
- 482 TSS: Temporary sponsored, pathway to PR
- Occupation lists: MLTSSL (medium-long term), STSOL (short term)

COMMON VISA REJECTIONS:
1. Insufficient funds proof
2. Incomplete documentation
3. Poor English scores
4. Job offer not meeting requirements
5. Criminal record not disclosed
6. Previous visa violations
7. Inconsistent information

DOCUMENT CHECKLIST:
- Valid passport (6+ months)
- Passport photos (specific size per country)
- Educational certificates & transcripts
- Work experience letters (detailed duties)
- Language test results (IELTS/TEF/PTE)
- Police clearance certificates
- Medical examination
- Proof of funds (bank statements 6 months)
- Marriage certificate (if applicable)
- Birth certificates

FINANCIAL REQUIREMENTS:
- Canada PR: CAD $13,310 for single, $16,570 for couple
- UK Skilled Worker: £1,270 in bank for 28 days
- USA H-1B: No minimum (employer sponsored)
- Australia 189: AUD $25,000+ recommended
- Germany: €11,208/year (€934/month)

PROCESSING TIMES (Approximate):
- Canada Express Entry: 6-8 months
- USA H-1B: 3-6 months after lottery
- UK Skilled Worker: 3 weeks (priority: 5 days)
- Germany Blue Card: 4-8 weeks
- Australia 189: 8-12 months
"""

# ========== AI CONVERSATION ENGINE ==========
class AIConversationEngine:
    """Gemini-powered empathetic conversation"""
    
    def __init__(self):
        self.conversation_history = {}  # Store per user
        
    async def generate_response(self, user_message: str, context: Dict) -> str:
        """Generate empathetic AI response"""
        try:
            # Build context-aware prompt
            current_date = datetime.now().strftime("%B %d, %Y")
            
            full_prompt = f"""
{PERSONALITY_PROMPT.format(current_date=current_date)}

KNOWLEDGE BASE:
{IMMIGRATION_KNOWLEDGE}

CONVERSATION CONTEXT:
- User said: "{user_message}"
- Chat type: {context.get('chat_type', 'private')}
- Detected topics: {', '.join(context.get('keywords', [])) if context.get('keywords') else 'General chat'}
- User name: {context.get('user_name', 'Friend')}

TASK:
Respond as Japa Genie - warm, personal, helpful. Reference specific knowledge when relevant.
Keep it conversational (2-4 sentences for casual chat, 5-8 for specific questions).
Show empathy, share brief experiences, give actionable advice.

YOUR RESPONSE:
"""
            
            # Generate with Gemini
            response = model.generate_content(full_prompt)
            
            # Clean up response
            ai_response = response.text.strip()
            
            # Ensure it's not too long (max 500 chars for group chat)
            if context.get('chat_type') != 'private' and len(ai_response) > 500:
                ai_response = ai_response[:497] + "..."
            
            logger.info(f"🤖 AI Response generated: {len(ai_response)} chars")
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ AI generation error: {e}")
            # Fallback to personality-driven template
            return self._fallback_response(user_message, context)
    
    def _fallback_response(self, message: str, context: Dict) -> str:
        """Fallback responses if AI fails"""
        visa_detected = len(context.get('keywords', [])) > 0
        
        if visa_detected:
            responses = [
                "Hey! That's a great question about immigration. I'm having a moment processing it properly - could you rephrase that for me? 😊",
                "I totally understand your concern! Give me a sec to gather my thoughts on this one - immigration can be complex!",
                "Good question! I want to give you the best advice, so let me think about that carefully. Can you give me more details about your specific situation?"
            ]
        else:
            responses = [
                "Thanks for sharing! I'm here if you need any immigration advice. 😊",
                "I hear you! Feel free to ask me anything about visas or relocation.",
                "That's interesting! Let me know if you need help with any immigration questions."
            ]
        
        return random.choice(responses)

# ========== SENTIMENT ANALYSIS ==========
class SentimentAnalyzer:
    """Detect emotional tone and respond appropriately"""
    
    def analyze(self, text: str) -> Dict:
        """Analyze sentiment and emotional state"""
        text_lower = text.lower()
        
        # Stress/Anxiety indicators
        stress_words = ['stressed', 'worried', 'anxious', 'scared', 'nervous', 'overwhelmed', 
                       'frustrated', 'confused', 'difficult', 'hard', 'struggling']
        
        # Positive/Excited indicators
        positive_words = ['excited', 'happy', 'approved', 'accepted', 'got it', 'success', 
                         'yes!', 'finally', 'approved', 'thank you']
        
        # Question indicators
        question_words = ['how', 'what', 'when', 'where', 'why', 'can', 'should', 'would', 
                         'is it', 'do i', 'help', '?']
        
        sentiment = {
            'is_stressed': any(word in text_lower for word in stress_words),
            'is_positive': any(word in text_lower for word in positive_words),
            'is_question': any(word in text_lower for word in question_words),
            'needs_empathy': False,
            'needs_celebration': False
        }
        
        # Determine response type
        if sentiment['is_stressed']:
            sentiment['needs_empathy'] = True
        if sentiment['is_positive']:
            sentiment['needs_celebration'] = True
            
        return sentiment

# ========== VISA INTELLIGENCE ==========
class VisaIntelligence:
    """Enhanced visa keyword detection"""
    
    def __init__(self):
        self.visa_keywords = [
            # Core terms
            "visa", "immigration", "immigrate", "migrate", "relocation", "relocate",
            "work permit", "residence permit", "green card", "citizenship", "passport",
            
            # Visa types
            "student visa", "tourist visa", "business visa", "work visa", "family visa",
            "skilled worker", "express entry", "provincial nominee", "h-1b", "l-1 visa",
            "eu blue card", "schengen", "tier 2", "skilled independent",
            
            # Process terms
            "visa application", "visa renewal", "sponsorship", "documentation",
            "consulate", "embassy", "interview", "biometrics", "medical exam",
            "police clearance", "background check", "coe", "certificate of eligibility",
            
            # Country-specific
            "canada pr", "usa green card", "uk visa", "australia pr", "germany visa",
            "japan visa", "residence card", "permanent residence", "temporary residence",
            
            # Common questions
            "how to apply", "visa requirements", "processing time", "visa fee",
            "ielts", "language test", "proof of funds", "job offer", "invitation letter"
        ]
        
    def detect(self, text: str) -> List[str]:
        """Detect visa-related keywords"""
        text_lower = text.lower()
        detected = []
        
        for keyword in self.visa_keywords:
            if keyword in text_lower:
                # Avoid false positives
                if keyword == "visa" and ("credit" in text_lower or "debit" in text_lower):
                    continue
                detected.append(keyword)
        
        return list(set(detected))  # Remove duplicates

# ========== FEEDBACK SYSTEM ==========
class FeedbackSystem:
    """Log conversations for improvement"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.feedback_channel_id = os.getenv("FEEDBACK_CHANNEL_ID", "@JapaGenieFeedback")
        self.local_storage = "visa_intelligence.jsonl"
        
    async def log_conversation(self, data: Dict):
        """Log important conversations"""
        try:
            # Save locally
            with open(self.local_storage, "a") as f:
                f.write(json.dumps(data) + "\n")
            
            # Send to Telegram channel if high priority
            if data.get('priority') == 'high':
                await self._send_to_channel(data)
                
            logger.info(f"📊 Logged: {data.get('user_name')} - {len(data.get('keywords', []))} keywords")
            
        except Exception as e:
            logger.error(f"❌ Logging error: {e}")
    
    async def _send_to_channel(self, data: Dict):
        """Send to feedback channel"""
        try:
            message = f"""
🚨 **HIGH PRIORITY CONVERSATION**

👤 User: {data.get('user_name')}
🔑 Keywords: {', '.join(data.get('keywords', [])[:5])}
💬 Message: {data.get('text', '')[:200]}...
😊 Sentiment: {data.get('sentiment', 'neutral')}
📍 Chat: {data.get('chat_title')}
🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            async with httpx.AsyncClient() as client:
                await client.post(url, json={
                    "chat_id": self.feedback_channel_id,
                    "text": message,
                    "parse_mode": "Markdown"
                })
        except Exception as e:
            logger.error(f"❌ Channel send error: {e}")

# ========== MAIN BOT ==========
class JapaGenieBot:
    """AI-Powered Japa Genie Bot"""
    
    def __init__(self):
        self.ai_engine = AIConversationEngine()
        self.sentiment = SentimentAnalyzer()
        self.visa_intel = VisaIntelligence()
        self.feedback = FeedbackSystem(TELEGRAM_BOT_TOKEN)
        
    async def process_message(self, update: Dict) -> Optional[str]:
        """Process incoming message with AI"""
        try:
            message = update.get("message", {})
            if not message:
                return None
            
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()
            user = message.get("from", {})
            chat_type = message.get("chat", {}).get("type", "private")
            chat_title = message.get("chat", {}).get("title", "Private Chat")
            
            if not text or text.startswith("/"):
                return None
            
            # Skip very short messages in groups
            if chat_type != "private" and len(text.split()) < 3:
                return None
            
            # Detect visa topics
            visa_keywords = self.visa_intel.detect(text)
            
            # Analyze sentiment
            sentiment_data = self.sentiment.analyze(text)
            
            # Build context for AI
            context = {
                "text": text,
                "user_name": user.get("first_name", "Friend"),
                "chat_type": chat_type,
                "keywords": visa_keywords,
                "sentiment": sentiment_data,
                "needs_empathy": sentiment_data.get('needs_empathy'),
                "needs_celebration": sentiment_data.get('needs_celebration')
            }
            
            # Log if visa-related or high emotion
            if visa_keywords or sentiment_data.get('needs_empathy') or sentiment_data.get('needs_celebration'):
                await self.feedback.log_conversation({
                    "user_id": user.get("id"),
                    "user_name": user.get("first_name"),
                    "username": user.get("username"),
                    "text": text,
                    "keywords": visa_keywords,
                    "sentiment": "stressed" if sentiment_data.get('needs_empathy') else "positive" if sentiment_data.get('needs_celebration') else "neutral",
                    "chat_id": chat_id,
                    "chat_title": chat_title,
                    "chat_type": chat_type,
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high" if sentiment_data.get('needs_empathy') else "normal"
                })
            
            # Decide if should respond (smart rate)
            should_respond = self._should_respond(context)
            
            if should_respond:
                # Generate AI response
                response = await self.ai_engine.generate_response(text, context)
                return response
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Process error: {e}")
            return None
    
    def _should_respond(self, context: Dict) -> bool:
        """Smart decision on whether to respond"""
        chat_type = context.get('chat_type')
        has_keywords = len(context.get('keywords', [])) > 0
        sentiment = context.get('sentiment', {})
        
        # Always respond in DMs
        if chat_type == "private":
            return True
        
        # Always respond to stress/questions
        if sentiment.get('needs_empathy') or sentiment.get('is_question'):
            return True
        
        # Always respond to celebrations
        if sentiment.get('needs_celebration'):
            return True
        
        # Respond to visa topics (40% rate)
        if has_keywords:
            return random.random() < 0.4
        
        # Respond to general chat (10% rate)
        return random.random() < 0.1

# Initialize bot
bot = JapaGenieBot()

# ========== FASTAPI ENDPOINTS ==========
@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """Main webhook handler"""
    try:
        update = await request.json()
        
        # Process in background to avoid timeout
        asyncio.create_task(process_and_respond(update))
        
        return JSONResponse({"ok": True})
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return JSONResponse({"ok": True})

async def process_and_respond(update: Dict):
    """Process message and send response (background task)"""
    try:
        response_text = await bot.process_message(update)
        
        if response_text:
            message = update.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            
            # Show typing
            await send_typing_action(chat_id)
            
            # Human-like delay
            await asyncio.sleep(random.uniform(1, 2.5))
            
            # Send response
            await send_telegram_message(chat_id, response_text)
            
    except Exception as e:
        logger.error(f"❌ Response error: {e}")

@app.get("/")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "bot": BOT_NAME,
        "version": VERSION,
        "personality": "Empathetic 32-year-old female immigration advisor",
        "ai_powered": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stats")
async def stats():
    """Bot statistics"""
    try:
        with open("visa_intelligence.jsonl", "r") as f:
            conversations = f.readlines()
        
        return {
            "total_conversations": len(conversations),
            "bot": BOT_NAME,
            "ai_model": "Gemini Pro",
            "personality": "Warm, empathetic female advisor"
        }
    except:
        return {"total_conversations": 0}

# ========== HELPERS ==========
async def send_telegram_message(chat_id: int, text: str):
    """Send message"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        async with httpx.AsyncClient() as client:
            await client.post(url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            })
    except Exception as e:
        logger.error(f"❌ Send error: {e}")

async def send_typing_action(chat_id: int):
    """Show typing indicator"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction"
        async with httpx.AsyncClient() as client:
            await client.post(url, json={
                "chat_id": chat_id,
                "action": "typing"
            })
    except:
        pass