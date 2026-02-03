# Agentic Honey-Pot for Scam Detection - Deployment Guide

## Overview
This is a complete AI-powered honeypot system that detects scam messages and autonomously engages scammers to extract intelligence without revealing detection.

## Features
✅ **Scam Detection**: Multi-pattern detection for bank fraud, UPI fraud, phishing, fake offers, impersonation, and OTP fraud
✅ **Agentic Engagement**: AI agent with multiple personas that adapts responses dynamically
✅ **Intelligence Extraction**: Automatically extracts bank accounts, UPI IDs, phishing links, phone numbers, and suspicious keywords
✅ **Multi-turn Conversations**: Handles complex conversations with context awareness
✅ **API Authentication**: Secure API key-based authentication
✅ **Automated Reporting**: Sends final intelligence to GUVI evaluation endpoint

## Quick Start

### 1. Installation

```bash
# Clone or download the files
cd honeypot-system

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your API key
nano .env
```

Set `API_SECRET_KEY` to your desired secret key (e.g., `hackathon-2024-secret-key`)

### 3. Local Testing

```bash
# Run the server
python honeypot_api.py

# Or with uvicorn directly
uvicorn honeypot_api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Test scam detection (replace YOUR_API_KEY with your actual key)
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "sessionId": "test-session-123",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately.",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

## Deployment Options

### Option 1: Deploy to Railway

1. Create account at https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variable: `API_SECRET_KEY=your-secret-key`
5. Railway will auto-detect Python and deploy
6. Your API endpoint: `https://your-app.railway.app/detect`

### Option 2: Deploy to Render

1. Create account at https://render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn honeypot_api:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `API_SECRET_KEY=your-secret-key`
6. Your API endpoint: `https://your-app.onrender.com/detect`

### Option 3: Deploy to Google Cloud Run

```bash
# Build Docker image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/honeypot-api

# Deploy
gcloud run deploy honeypot-api \
  --image gcr.io/YOUR_PROJECT_ID/honeypot-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_SECRET_KEY=your-secret-key
```

### Option 4: Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-honeypot-api

# Set environment variable
heroku config:set API_SECRET_KEY=your-secret-key

# Deploy
git push heroku main
```

## API Documentation

### Endpoint: POST /detect

**Headers:**
```
x-api-key: YOUR_SECRET_API_KEY
Content-Type: application/json
```

**Request Body:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Message text here",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Agent's response here"
}
```

## System Architecture

### 1. Scam Detection Engine
- Pattern-based detection using regex
- Heuristic scoring based on urgency, threats, and action words
- Categorizes scams into 6 types:
  - Bank Fraud
  - UPI Fraud
  - Phishing
  - Fake Offers
  - Impersonation
  - OTP Fraud

### 2. AI Agent
- Multiple personas (concerned elderly, busy professional, trusting user, cautious user)
- Stage-based engagement (initial, probing, hesitant, final)
- Context-aware responses
- Natural language generation

### 3. Intelligence Extraction
- Bank account numbers
- UPI IDs
- Phishing links and URLs
- Phone numbers
- Suspicious keywords

### 4. Session Management
- Tracks conversation history
- Maintains extracted intelligence
- Manages engagement state
- Determines when to conclude

### 5. Reporting
- Automatically sends final report to GUVI endpoint
- Includes all extracted intelligence
- Provides engagement summary

## Advanced Features

### Custom Scam Patterns
Add new patterns in `ScamDetector.SCAM_PATTERNS`:
```python
'new_scam_type': [
    r'pattern1',
    r'pattern2'
]
```

### Custom Personas
Add new personas in `HoneypotAgent.personas`:
```python
'persona_name': "Description of persona behavior"
```

### Engagement Strategies
Modify response generation in:
- `_generate_initial_response()`: First contact
- `_generate_probing_response()`: Information gathering
- `_generate_hesitant_response()`: Building trust
- `_generate_final_response()`: Conclusion

## Monitoring & Debugging

### View Logs
```bash
# With uvicorn
uvicorn honeypot_api:app --log-level debug

# View session data (add to code)
print(session_manager.sessions)
```

### Health Check
```bash
curl http://your-api-url/health
```

## Security Considerations

✅ API key authentication on all endpoints
✅ Input validation with Pydantic models
✅ No storage of sensitive user data
✅ Ethical engagement (no impersonation of real individuals)
✅ Responsible intelligence handling

## Evaluation Criteria Met

1. ✅ **Scam Detection Accuracy**: Multi-pattern detection with heuristics
2. ✅ **Agentic Engagement Quality**: Context-aware, multi-persona responses
3. ✅ **Intelligence Extraction**: Comprehensive regex-based extraction
4. ✅ **API Stability**: FastAPI with error handling
5. ✅ **Ethical Behavior**: No impersonation, responsible data handling

## Troubleshooting

**Problem**: API returns 401 Unauthorized
**Solution**: Check that x-api-key header matches your API_SECRET_KEY

**Problem**: Agent responses seem repetitive
**Solution**: Increase persona variety or add more response templates

**Problem**: Intelligence not extracted
**Solution**: Check regex patterns match your test data format

**Problem**: Final callback not sent
**Solution**: Verify engagement_count reaches threshold (7+ messages)

## Testing Scenarios

### Scenario 1: Bank Fraud
```json
{
  "message": {
    "text": "Your bank account will be blocked. Verify at http://fake-bank.com"
  }
}
```
Expected: Detects bank_fraud, extracts phishing link

### Scenario 2: UPI Fraud
```json
{
  "message": {
    "text": "Share your UPI ID scammer@paytm to receive refund"
  }
}
```
Expected: Detects upi_fraud, extracts UPI ID

### Scenario 3: OTP Fraud
```json
{
  "message": {
    "text": "Share the 6-digit OTP sent to your phone for verification"
  }
}
```
Expected: Detects otp_fraud, probes for more info

## Support

For questions or issues:
1. Check the logs for error messages
2. Verify API key configuration
3. Test with provided example requests
4. Review scam detection patterns

## License
This project is created for the GUVI Hackathon and is intended for educational and security research purposes only.