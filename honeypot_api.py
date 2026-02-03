"""
Agentic Honey-Pot for Scam Detection & Intelligence Extraction
FastAPI-based REST API that detects scam messages and engages scammers autonomously
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import re
import requests
from datetime import datetime
import asyncio
import os
from enum import Enum
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-api-key-here")
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

app = FastAPI(title="Agentic Honey-Pot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon evaluation
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Models ====================

class MessageSender(str, Enum):
    SCAMMER = "scammer"
    USER = "user"

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class Metadata(BaseModel):
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"

class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata: Optional[Metadata] = None

class HoneypotResponse(BaseModel):
    status: str
    reply: str

class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)

class FinalResultPayload(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: Dict[str, List[str]]
    agentNotes: str

# ==================== Session Management ====================

class SessionManager:
    """Manages conversation sessions and extracted intelligence"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "intelligence": ExtractedIntelligence(),
                "scam_detected": False,
                "engagement_count": 0,
                "should_continue": True,
                "scam_type": None
            }
        return self.sessions[session_id]
    
    def update_intelligence(self, session_id: str, text: str):
        """Extract intelligence from text"""
        session = self.get_session(session_id)
        intel = session["intelligence"]
        
        # Extract bank accounts (various formats)
        # 16-digit format with optional separators
        bank_accounts = re.findall(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', text)
        # 9-18 digit account numbers
        bank_accounts += re.findall(r'\b\d{9,18}\b', text)
        # IFSC-like patterns
        bank_accounts += re.findall(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', text.upper())
        intel.bankAccounts.extend([acc.replace(" ", "").replace("-", "") for acc in bank_accounts])
        
        # Extract UPI IDs - comprehensive list
        upi_patterns = [
            r'\b[\w\.-]+@paytm\b',
            r'\b[\w\.-]+@phonepe\b',
            r'\b[\w\.-]+@gpay\b',
            r'\b[\w\.-]+@upi\b',
            r'\b[\w\.-]+@ybl\b',
            r'\b[\w\.-]+@oksbi\b',
            r'\b[\w\.-]+@okaxis\b',
            r'\b[\w\.-]+@okicici\b',
            r'\b[\w\.-]+@okhdfcbank\b',
            r'\b[\w\.-]+@okbizaxis\b',
            r'\b[\w\.-]+@ibl\b',
            r'\b[\w\.-]+@axl\b',
        ]
        for pattern in upi_patterns:
            upi_ids = re.findall(pattern, text.lower())
            intel.upiIds.extend(upi_ids)
        
        # Extract URLs and potential phishing links
        urls = re.findall(r'https?://[^\s]+', text)
        urls += re.findall(r'www\.[^\s]+', text)
        # Domain patterns
        urls += re.findall(r'\b[\w-]+\.(?:com|in|org|net|co\.in|xyz|click|top|online|site|info|biz)[^\s]*', text)
        intel.phishingLinks.extend(urls)
        
        # Extract phone numbers (Indian and international formats)
        phones = re.findall(r'\+91[-\s]?\d{10}', text)
        phones += re.findall(r'\+\d{1,4}[-\s]?\d{10}', text)
        phones += re.findall(r'\b\d{10}\b', text)
        phones += re.findall(r'\b0\d{10}\b', text)  # Numbers starting with 0
        intel.phoneNumbers.extend(phones)
        
        # Extract suspicious keywords - comprehensive list
        suspicious_words = [
            'urgent', 'verify', 'blocked', 'suspended', 'immediately', 'confirm',
            'account', 'bank', 'upi', 'payment', 'transfer', 'otp', 'password',
            'click here', 'limited time', 'act now', 'prize', 'winner', 'congratulations',
            'refund', 'tax', 'penalty', 'arrest', 'legal action', 'freeze',
            'kyc', 'update', 'expired', 'deactivated', 'unauthorized', 'suspicious',
            'claim', 'reward', 'lottery', 'won', 'cashback', 'offer', 'deal',
            'hurry', 'last chance', 'final notice', 'warrant', 'court', 'police',
            'customs', 'delivery', 'parcel', 'package', 'courier', 'fedex', 'dhl',
            'amazon', 'flipkart', 'security', 'code', 'pin', 'cvv', 'card',
            'government', 'official', 'department', 'notice', 'billing', 'invoice'
        ]
        
        text_lower = text.lower()
        found_keywords = [word for word in suspicious_words if word in text_lower]
        intel.suspiciousKeywords.extend(found_keywords)
        
        # Remove duplicates while preserving order
        intel.bankAccounts = list(dict.fromkeys(intel.bankAccounts))
        intel.upiIds = list(dict.fromkeys(intel.upiIds))
        intel.phishingLinks = list(dict.fromkeys(intel.phishingLinks))
        intel.phoneNumbers = list(dict.fromkeys(intel.phoneNumbers))
        intel.suspiciousKeywords = list(dict.fromkeys(intel.suspiciousKeywords))

session_manager = SessionManager()

# ==================== Scam Detection ====================

class ScamDetector:
    """Detects scam intent from messages"""
    
    SCAM_PATTERNS = {
        'bank_fraud': [
            r'bank account.*(?:blocked|suspended|frozen)',
            r'verify.*(?:account|identity|details)',
            r'account.*(?:deactivated|locked|closed)',
            r'update.*(?:kyc|pan|aadhar)',
            r'unauthorized.*transaction'
        ],
        'upi_fraud': [
            r'upi.*(?:blocked|suspended)',
            r'share.*upi.*id',
            r'send.*money.*verify',
            r'payment.*pending',
            r'refund.*upi'
        ],
        'phishing': [
            r'click.*link.*(?:verify|update|confirm)',
            r'download.*app.*urgently',
            r'install.*certificate',
            r'login.*(?:immediately|now|urgent)',
            r'reset.*password.*click'
        ],
        'fake_offers': [
            r'congratulations.*(?:won|winner|prize)',
            r'lottery.*won',
            r'claim.*(?:prize|reward|gift)',
            r'limited.*time.*offer',
            r'exclusive.*deal.*today'
        ],
        'impersonation': [
            r'(?:police|court|tax|income tax|gst).*(?:notice|penalty|arrest)',
            r'legal.*action.*against',
            r'warrant.*issued',
            r'customs.*clearance',
            r'government.*(?:refund|scheme)'
        ],
        'otp_fraud': [
            r'share.*otp',
            r'send.*code.*verification',
            r'otp.*(?:expire|valid)',
            r'confirmation.*code',
            r'security.*code.*verify'
        ]
    }
    
    def detect(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Returns (is_scam, scam_type)
        """
        text_lower = text.lower()
        
        # First check pattern-based detection
        for scam_type, patterns in self.SCAM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return True, scam_type
        
        # Additional heuristics for sophisticated scams
        urgency_words = ['urgent', 'immediately', 'now', 'today', 'asap', 'quickly', 'hurry', 'fast', 'soon', 'expire', 'limited time']
        threat_words = ['blocked', 'suspended', 'arrested', 'penalty', 'legal action', 'freeze', 'deactivated', 'locked', 'cancelled', 'terminated']
        action_words = ['verify', 'confirm', 'click', 'share', 'send', 'update', 'provide', 'submit', 'enter', 'transfer']
        request_words = ['account', 'password', 'otp', 'code', 'upi', 'card', 'cvv', 'pin', 'aadhar', 'pan']
        
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        threat_count = sum(1 for word in threat_words if word in text_lower)
        action_count = sum(1 for word in action_words if word in text_lower)
        request_count = sum(1 for word in request_words if word in text_lower)
        
        # Check for URLs (often phishing)
        has_url = bool(re.search(r'https?://|www\.|\w+\.(com|in|org|net|xyz|click|top)', text_lower))
        
        # Check for UPI IDs
        has_upi = bool(re.search(r'@(paytm|phonepe|gpay|upi|ybl|oksbi|okaxis|okicici)', text_lower))
        
        # Check for phone numbers
        has_phone = bool(re.search(r'\+?\d{10,}', text))
        
        # Scam score heuristic (improved)
        scam_score = (
            urgency_count * 2 + 
            threat_count * 3 + 
            action_count * 1.5 + 
            request_count * 2 +
            (3 if has_url else 0) +
            (2 if has_upi else 0) +
            (1 if has_phone else 0)
        )
        
        # Lower threshold for better detection
        if scam_score >= 4:
            return True, 'generic_scam'
        
        return False, None

scam_detector = ScamDetector()

# ==================== AI Agent ====================

class HoneypotAgent:
    """AI Agent that engages scammers in human-like conversations"""
    
    def __init__(self):
        self.personas = {
            'concerned_elderly': "You are a 65-year-old person who is not very tech-savvy but concerned about their bank account. You ask questions cautiously and seem worried. You make occasional typos and use simple language.",
            'busy_professional': "You are a busy professional who is multitasking. You're initially skeptical but might be convinced with the right urgency. You respond quickly and sometimes impatiently.",
            'trusting_user': "You are a regular person who tends to trust official-sounding messages. You ask clarifying questions but are inclined to comply if it seems legitimate.",
            'cautious_user': "You are somewhat suspicious but willing to engage to understand what's happening. You ask for specific details and verification."
        }
    
    async def generate_response(self, session_id: str, conversation_history: List[Message], current_message: str, scam_type: str) -> str:
        """Generate a human-like response to keep the scammer engaged"""
        
        session = session_manager.get_session(session_id)
        engagement_count = session["engagement_count"]
        
        # Select persona based on scam type
        if scam_type in ['bank_fraud', 'upi_fraud']:
            persona_key = 'concerned_elderly' if engagement_count < 3 else 'cautious_user'
        elif scam_type == 'fake_offers':
            persona_key = 'trusting_user'
        else:
            persona_key = 'busy_professional'
        
        persona = self.personas[persona_key]
        
        # Build conversation context
        context = self._build_context(conversation_history, current_message)
        
        # Generate response based on engagement stage
        if engagement_count == 0:
            # Initial response - show concern/interest
            response = self._generate_initial_response(current_message, scam_type)
        elif engagement_count < 3:
            # Early engagement - ask questions to extract info
            response = self._generate_probing_response(current_message, scam_type, context)
        elif engagement_count < 6:
            # Mid engagement - show willingness but hesitation
            response = self._generate_hesitant_response(current_message, scam_type, context)
        else:
            # Late engagement - extract final details or wrap up
            response = self._generate_final_response(session_id, current_message, scam_type, context)
        
        return response
    
    def _build_context(self, history: List[Message], current: str) -> str:
        """Build conversation context"""
        context = ""
        for msg in history[-3:]:  # Last 3 messages
            context += f"{msg.sender}: {msg.text}\n"
        context += f"scammer: {current}\n"
        return context
    
    def _generate_initial_response(self, message: str, scam_type: str) -> str:
        """Generate initial response showing concern or interest"""
        
        responses = {
            'bank_fraud': [
                "Oh no! Why will my account be blocked? I haven't done anything wrong.",
                "What? Is this a message from my bank? I'm worried now.",
                "I don't understand. Can you explain what's happening with my account?"
            ],
            'upi_fraud': [
                "My UPI is blocked? But I just used it yesterday. What happened?",
                "Is this from my bank? I need to use UPI for payments.",
                "Why would my UPI be suspended? Please tell me what to do."
            ],
            'phishing': [
                "I got your message. Is this urgent? Should I click the link now?",
                "What kind of verification is this? I want to make sure it's safe.",
                "Ok, but can you tell me more about what I need to do?"
            ],
            'fake_offers': [
                "Really? I won something? What prize is this?",
                "This sounds great! How do I claim it?",
                "Wow, I didn't know I entered any lottery. What do I need to do?"
            ],
            'impersonation': [
                "Legal notice? What have I done wrong? I'm scared.",
                "Is this really from the government? What should I do?",
                "I don't want any legal trouble. Please help me understand."
            ],
            'otp_fraud': [
                "OTP? I just received one. Is this related to my account?",
                "Should I share the code? I'm not sure what this is for.",
                "I got a code but I didn't request anything. What's going on?"
            ]
        }
        
        import random
        response_list = responses.get(scam_type, responses['bank_fraud'])
        return random.choice(response_list)
    
    def _generate_probing_response(self, message: str, scam_type: str, context: str) -> str:
        """Generate response that probes for more information"""
        
        # Extract what scammer is asking for
        message_lower = message.lower()
        
        # Context-aware probing based on keywords
        if 'account' in message_lower or 'number' in message_lower:
            responses = [
                "Which account number do you need? I have multiple accounts.",
                "Should I share my savings account or current account number?",
                "I have accounts in different banks. Which one are you asking about?"
            ]
        elif 'upi' in message_lower:
            responses = [
                "What UPI ID exactly? I have different ones for different apps.",
                "I use multiple UPI apps. Which one should I share - PhonePe, GPay, or Paytm?",
                "My UPI ID is linked to many apps. Can you specify which one?"
            ]
        elif 'click' in message_lower or 'link' in message_lower:
            responses = [
                "I'm trying to click but the link doesn't work. Can you send it again?",
                "The link is not opening on my phone. Is there another way?",
                "I clicked the link but nothing happened. What should I do?"
            ]
        elif 'otp' in message_lower or 'code' in message_lower:
            responses = [
                "I received a code but it's not clear. Should I share all the digits?",
                "The OTP is 6 digits, right? Should I tell you the whole thing?",
                "I got the code. Do you need me to read it out to you?"
            ]
        elif 'payment' in message_lower or 'money' in message_lower or 'send' in message_lower or 'transfer' in message_lower:
            responses = [
                "How much should I send? And to which account or UPI?",
                "What amount exactly? And will I get it back?",
                "Should I use UPI or bank transfer? What's the account details?"
            ]
        elif 'install' in message_lower or 'download' in message_lower:
            responses = [
                "What app should I download? Can you give me the exact name?",
                "Is this app available on Play Store? What's it called?",
                "Should I download it from the link you sent or from the app store?"
            ]
        elif 'call' in message_lower or 'contact' in message_lower or 'phone' in message_lower:
            responses = [
                "What number should I call? And what should I say?",
                "Should I call you right now? What's your number?",
                "I can call, but what extension or department should I ask for?"
            ]
        elif 'card' in message_lower or 'cvv' in message_lower or 'debit' in message_lower or 'credit' in message_lower:
            responses = [
                "Which card - my debit card or credit card?",
                "You need the card number? All 16 digits?",
                "Should I also share the expiry date and CVV?"
            ]
        elif 'kyc' in message_lower or 'document' in message_lower or 'aadhar' in message_lower or 'pan' in message_lower:
            responses = [
                "What documents do you need? I have Aadhar and PAN card.",
                "Should I upload the documents somewhere? Where?",
                "Do you need photos of my documents or just the numbers?"
            ]
        else:
            responses = [
                "Can you please provide more details? I want to do this correctly.",
                "I'm not sure I understand. Can you explain step by step?",
                "What exactly do you need from me to resolve this?",
                "I want to help but need clearer instructions. What's the next step?"
            ]
        
        import random
        return random.choice(responses)
    
    def _generate_hesitant_response(self, message: str, scam_type: str, context: str) -> str:
        """Generate response showing hesitation but willingness"""
        
        message_lower = message.lower()
        
        responses = [
            "I'm a bit confused. Can you confirm you're from the official bank?",
            "My friend said to be careful with such messages. But this is real, right?",
            "Before I proceed, can you give me your employee ID or official number?",
            "I want to help but I need to verify this is legitimate. What's your department?",
            "Okay, but can I call my bank first to confirm this?",
            "This seems urgent but I want to be sure. What happens if I don't do this now?"
        ]
        
        import random
        return random.choice(responses)
    
    def _generate_final_response(self, session_id: str, message: str, scam_type: str, context: str) -> str:
        """Generate final response to extract last details or conclude"""
        
        responses = [
            "I'm going to check with my bank branch directly. Thank you for informing me.",
            "I think I should visit the bank in person for this. Thanks anyway.",
            "My son said this might be a scam. I'll verify with the bank first.",
            "I'm not comfortable sharing this information online. I'll go to the bank.",
            "Let me consult with someone before proceeding. I'll get back to you.",
            "I received a call from my bank saying this is fake. I'm reporting this."
        ]
        
        import random
        session = session_manager.get_session(session_id)
        session["should_continue"] = False
        
        return random.choice(responses)

honeypot_agent = HoneypotAgent()

# ==================== API Endpoints ====================

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """Middleware to verify API key"""
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
        return await call_next(request)
    
    api_key = request.headers.get("x-api-key")
    if api_key != API_SECRET_KEY:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing API key"}
        )
    
    return await call_next(request)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Agentic Honey-Pot API"}

@app.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """Get session status and intelligence (for debugging/monitoring)"""
    if session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_manager.sessions[session_id]
    intelligence = session["intelligence"]
    
    return {
        "sessionId": session_id,
        "scamDetected": session["scam_detected"],
        "scamType": session["scam_type"],
        "engagementCount": session["engagement_count"],
        "totalMessages": len(session["messages"]),
        "shouldContinue": session["should_continue"],
        "extractedIntelligence": {
            "bankAccounts": len(intelligence.bankAccounts),
            "upiIds": len(intelligence.upiIds),
            "phishingLinks": len(intelligence.phishingLinks),
            "phoneNumbers": len(intelligence.phoneNumbers),
            "suspiciousKeywords": len(intelligence.suspiciousKeywords)
        }
    }

@app.post("/detect", response_model=HoneypotResponse)
async def detect_and_engage(request: HoneypotRequest):
    """
    Main endpoint that receives messages, detects scams, and engages scammers
    """
    try:
        session_id = request.sessionId
        current_message = request.message
        conversation_history = request.conversationHistory
        
        logger.info(f"📨 Session {session_id}: Received message from {current_message.sender}")
        
        # Get or create session
        session = session_manager.get_session(session_id)
        
        # Add current message to session
        session["messages"].append(current_message)
        
        # Extract intelligence from scammer's message
        session_manager.update_intelligence(session_id, current_message.text)
        
        # Detect scam intent
        is_scam, scam_type = scam_detector.detect(current_message.text)
        
        if is_scam and not session["scam_detected"]:
            session["scam_detected"] = True
            session["scam_type"] = scam_type
            logger.info(f"🚨 Session {session_id}: Scam detected - Type: {scam_type}")
        
        # Generate response
        if session["scam_detected"] and session["should_continue"]:
            # AI Agent generates human-like response
            agent_response = await honeypot_agent.generate_response(
                session_id,
                conversation_history,
                current_message.text,
                session["scam_type"]
            )
            
            session["engagement_count"] += 1
            logger.info(f"🤖 Session {session_id}: Agent response #{session['engagement_count']}")
            
            # Add agent response to session
            agent_message = Message(
                sender="user",
                text=agent_response,
                timestamp=int(datetime.now().timestamp() * 1000)
            )
            session["messages"].append(agent_message)
            
            # Check if we should send final callback
            if session["engagement_count"] >= 7 or not session["should_continue"]:
                logger.info(f"📊 Session {session_id}: Triggering final callback")
                # Send final result to GUVI
                await send_final_result(session_id)
            
            return HoneypotResponse(
                status="success",
                reply=agent_response
            )
        else:
            # Not a scam or engagement ended
            logger.info(f"✅ Session {session_id}: Non-scam message or engagement ended")
            return HoneypotResponse(
                status="success",
                reply="Thank you for your message. Have a nice day!"
            )
    
    except Exception as e:
        logger.error(f"❌ Session {session_id if 'session_id' in locals() else 'unknown'}: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def send_final_result(session_id: str):
    """Send final intelligence report to GUVI evaluation endpoint"""
    session = session_manager.get_session(session_id)
    
    # Prevent duplicate sends
    if session.get("final_result_sent", False):
        logger.warning(f"⚠️ Session {session_id}: Final result already sent, skipping")
        return
    
    try:
        intelligence = session["intelligence"]
        
        # Prepare payload
        payload = {
            "sessionId": session_id,
            "scamDetected": session["scam_detected"],
            "totalMessagesExchanged": len(session["messages"]),
            "extractedIntelligence": {
                "bankAccounts": intelligence.bankAccounts,
                "upiIds": intelligence.upiIds,
                "phishingLinks": intelligence.phishingLinks,
                "phoneNumbers": intelligence.phoneNumbers,
                "suspiciousKeywords": intelligence.suspiciousKeywords
            },
            "agentNotes": f"Scam type: {session['scam_type']}. Agent engaged scammer through {session['engagement_count']} turns using adaptive conversation strategies. Successfully extracted {len(intelligence.bankAccounts)} bank accounts, {len(intelligence.upiIds)} UPI IDs, {len(intelligence.phishingLinks)} phishing links, and {len(intelligence.phoneNumbers)} phone numbers."
        }
        
        logger.info(f"📤 Session {session_id}: Sending final result to GUVI")
        logger.debug(f"Payload: {payload}")
        
        # Send to GUVI with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    GUVI_CALLBACK_URL,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ Session {session_id}: Final result sent successfully (status: {response.status_code})")
                    session["final_result_sent"] = True
                    return
                else:
                    logger.warning(f"⚠️ Session {session_id}: Attempt {attempt + 1}/{max_retries} - Status {response.status_code}")
                    logger.debug(f"Response: {response.text}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⚠️ Session {session_id}: Attempt {attempt + 1}/{max_retries} - Request timeout")
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Session {session_id}: Attempt {attempt + 1}/{max_retries} - Error: {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"⏳ Session {session_id}: Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
        
        logger.error(f"❌ Session {session_id}: Failed to send final result after {max_retries} attempts")
        
    except Exception as e:
        logger.error(f"❌ Session {session_id}: Critical error sending final result: {str(e)}", exc_info=True)

# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(
        "honeypot_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )