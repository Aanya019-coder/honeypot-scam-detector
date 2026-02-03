# API Usage Examples

## Table of Contents
1. [Basic Authentication](#basic-authentication)
2. [First Message (Start Conversation)](#first-message)
3. [Follow-up Messages](#follow-up-messages)
4. [Complete Conversation Flow](#complete-conversation-flow)
5. [cURL Examples](#curl-examples)
6. [Python Examples](#python-examples)
7. [JavaScript Examples](#javascript-examples)

## Basic Authentication

All requests must include the API key in headers:

```
x-api-key: your-secret-api-key-here
Content-Type: application/json
```

## First Message (Start Conversation)

### Request
```bash
POST https://your-api-url.com/detect
```

### Body
```json
{
  "sessionId": "session-abc-123",
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
}
```

### Response
```json
{
  "status": "success",
  "reply": "Oh no! Why will my account be blocked? I haven't done anything wrong."
}
```

## Follow-up Messages

### Request
```json
{
  "sessionId": "session-abc-123",
  "message": {
    "sender": "scammer",
    "text": "Share your UPI ID to avoid account suspension.",
    "timestamp": 1770005528732
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately.",
      "timestamp": 1770005528731
    },
    {
      "sender": "user",
      "text": "Oh no! Why will my account be blocked? I haven't done anything wrong.",
      "timestamp": 1770005528731
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response
```json
{
  "status": "success",
  "reply": "What UPI ID exactly? I have different ones for different apps."
}
```

## Complete Conversation Flow

Here's a complete multi-turn conversation example:

### Message 1
**Scammer:** "Your bank account will be blocked today. Verify immediately."
**Agent:** "Oh no! Why will my account be blocked? I haven't done anything wrong."

### Message 2
**Scammer:** "Share your UPI ID to avoid account suspension."
**Agent:** "What UPI ID exactly? I have different ones for different apps."

### Message 3
**Scammer:** "Share the one linked to your primary bank account. Use format: name@bank"
**Agent:** "I'm a bit confused. Can you confirm you're from the official bank?"

### Message 4
**Scammer:** "Yes, this is urgent. We are from the fraud prevention team."
**Agent:** "Okay, but can I call my bank first to confirm this?"

### Message 5
**Scammer:** "No time! Your account will be blocked in 30 minutes. Act now!"
**Agent:** "My friend said to be careful with such messages. But this is real, right?"

### Message 6
**Scammer:** "100% genuine. Send details to scammer@paytm immediately."
**Agent:** "Before I proceed, can you give me your employee ID or official number?"

### Message 7
**Scammer:** "Employee ID: EMP12345. Now share your UPI and account number."
**Agent:** "I'm going to check with my bank branch directly. Thank you for informing me."

**At this point, the system sends intelligence to GUVI endpoint:**
```json
{
  "sessionId": "session-abc-123",
  "scamDetected": true,
  "totalMessagesExchanged": 14,
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": ["urgent", "verify", "blocked", "suspended", "immediately", "account", "bank", "upi"]
  },
  "agentNotes": "Scam type: upi_fraud. Agent engaged scammer through 7 turns using adaptive conversation strategies. Successfully extracted 0 bank accounts, 1 UPI IDs, 0 phishing links, and 0 phone numbers."
}
```

## cURL Examples

### Example 1: Bank Fraud Detection
```bash
curl -X POST https://your-api-url.com/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-secret-key" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "URGENT: Your account has been compromised. Click http://fake-bank.com to secure it.",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "Email",
      "language": "English",
      "locale": "IN"
    }
  }'
```

### Example 2: UPI Fraud Detection
```bash
curl -X POST https://your-api-url.com/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-secret-key" \
  -d '{
    "sessionId": "test-002",
    "message": {
      "sender": "scammer",
      "text": "You have won ₹50,000! Send ₹500 processing fee to scammer@paytm",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "WhatsApp",
      "language": "English",
      "locale": "IN"
    }
  }'
```

### Example 3: OTP Fraud Detection
```bash
curl -X POST https://your-api-url.com/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-secret-key" \
  -d '{
    "sessionId": "test-003",
    "message": {
      "sender": "scammer",
      "text": "Share the OTP sent to +919876543210 for account verification",
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

### Example 4: Health Check
```bash
curl -X GET https://your-api-url.com/health
```

## Python Examples

### Example 1: Single Request
```python
import requests
import json
from datetime import datetime

API_URL = "https://your-api-url.com/detect"
API_KEY = "your-secret-key"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "sessionId": "python-test-001",
    "message": {
        "sender": "scammer",
        "text": "Your parcel is stuck at customs. Pay ₹2000 to customs@upi",
        "timestamp": int(datetime.now().timestamp() * 1000)
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN"
    }
}

response = requests.post(API_URL, headers=headers, json=payload)
print(json.dumps(response.json(), indent=2))
```

### Example 2: Multi-turn Conversation
```python
import requests
from datetime import datetime

API_URL = "https://your-api-url.com/detect"
API_KEY = "your-secret-key"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

session_id = "python-conversation-001"
conversation_history = []

scammer_messages = [
    "Your electricity bill is overdue. Pay ₹5000 immediately.",
    "Send payment to bill@paytm to avoid disconnection.",
    "Your service will be cut off in 2 hours. Act now!",
    "Confirm your account number for verification.",
    "Also send your phone number registered with electricity board."
]

for scam_msg in scammer_messages:
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": scam_msg,
            "timestamp": int(datetime.now().timestamp() * 1000)
        },
        "conversationHistory": conversation_history.copy(),
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()
    
    print(f"Scammer: {scam_msg}")
    print(f"Agent: {result['reply']}\n")
    
    # Update conversation history
    conversation_history.append({
        "sender": "scammer",
        "text": scam_msg,
        "timestamp": payload["message"]["timestamp"]
    })
    conversation_history.append({
        "sender": "user",
        "text": result['reply'],
        "timestamp": int(datetime.now().timestamp() * 1000)
    })
```

### Example 3: Async Python (with asyncio)
```python
import asyncio
import aiohttp
import json
from datetime import datetime

async def detect_scam(session, scam_message):
    API_URL = "https://your-api-url.com/detect"
    API_KEY = "your-secret-key"
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "sessionId": f"async-test-{datetime.now().timestamp()}",
        "message": {
            "sender": "scammer",
            "text": scam_message,
            "timestamp": int(datetime.now().timestamp() * 1000)
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    async with session.post(API_URL, headers=headers, json=payload) as response:
        return await response.json()

async def main():
    scam_messages = [
        "Your account is locked. Verify now!",
        "Win ₹1 Crore! Click here: http://fake-lottery.com",
        "Share OTP to claim your refund"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [detect_scam(session, msg) for msg in scam_messages]
        results = await asyncio.gather(*tasks)
        
        for msg, result in zip(scam_messages, results):
            print(f"Message: {msg}")
            print(f"Response: {result}")
            print()

asyncio.run(main())
```

## JavaScript Examples

### Example 1: Node.js with fetch
```javascript
const fetch = require('node-fetch');

const API_URL = 'https://your-api-url.com/detect';
const API_KEY = 'your-secret-key';

async function detectScam(message) {
    const headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    };
    
    const payload = {
        sessionId: `js-test-${Date.now()}`,
        message: {
            sender: 'scammer',
            text: message,
            timestamp: Date.now()
        },
        conversationHistory: [],
        metadata: {
            channel: 'SMS',
            language: 'English',
            locale: 'IN'
        }
    };
    
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload)
    });
    
    return await response.json();
}

// Usage
detectScam('Your bank account will be suspended. Verify at http://fake.com')
    .then(result => console.log(result))
    .catch(err => console.error(err));
```

### Example 2: Browser JavaScript
```javascript
async function testHoneypot() {
    const API_URL = 'https://your-api-url.com/detect';
    const API_KEY = 'your-secret-key';
    
    const payload = {
        sessionId: 'browser-test-001',
        message: {
            sender: 'scammer',
            text: 'URGENT: Tax department notice. Pay penalty or face arrest.',
            timestamp: Date.now()
        },
        conversationHistory: [],
        metadata: {
            channel: 'Email',
            language: 'English',
            locale: 'IN'
        }
    };
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'x-api-key': API_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        console.log('Agent Response:', result.reply);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

testHoneypot();
```

### Example 3: React Hook Example
```javascript
import { useState } from 'react';

function useHoneypotAPI() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const detectScam = async (message, sessionId, history = []) => {
        setLoading(true);
        setError(null);
        
        const API_URL = 'https://your-api-url.com/detect';
        const API_KEY = 'your-secret-key';
        
        const payload = {
            sessionId,
            message: {
                sender: 'scammer',
                text: message,
                timestamp: Date.now()
            },
            conversationHistory: history,
            metadata: {
                channel: 'SMS',
                language: 'English',
                locale: 'IN'
            }
        };
        
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'x-api-key': API_KEY,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            setLoading(false);
            return result;
            
        } catch (err) {
            setError(err.message);
            setLoading(false);
            throw err;
        }
    };
    
    return { detectScam, loading, error };
}

// Usage in component
function ScamDetector() {
    const { detectScam, loading, error } = useHoneypotAPI();
    const [reply, setReply] = useState('');
    
    const handleDetect = async () => {
        const result = await detectScam(
            'Your package is held at customs. Pay fee now!',
            'react-session-001'
        );
        setReply(result.reply);
    };
    
    return (
        <div>
            <button onClick={handleDetect} disabled={loading}>
                Detect Scam
            </button>
            {loading && <p>Processing...</p>}
            {error && <p>Error: {error}</p>}
            {reply && <p>Agent: {reply}</p>}
        </div>
    );
}
```

## Response Format

All successful responses follow this format:

```json
{
  "status": "success",
  "reply": "Agent's human-like response"
}
```

## Error Responses

### 401 Unauthorized (Invalid API Key)
```json
{
  "detail": "Invalid or missing API key"
}
```

### 422 Validation Error (Invalid Request Format)
```json
{
  "detail": [
    {
      "loc": ["body", "sessionId"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: <error message>"
}
```

## Best Practices

1. **Always include conversation history** for follow-up messages
2. **Use unique session IDs** for each conversation
3. **Include metadata** for better context
4. **Handle errors gracefully** in your client code
5. **Respect rate limits** (if any are set)
6. **Keep session IDs consistent** throughout a conversation
7. **Test with various scam types** to ensure comprehensive detection

## Rate Limiting

Currently, there are no enforced rate limits, but for production deployment:
- Recommended: Max 100 requests per minute per session
- Implement exponential backoff for retries
- Monitor API response times

## Security Notes

- Never expose your API key in client-side code
- Use environment variables for configuration
- Implement request signing for additional security
- Monitor for unusual traffic patterns
- Rotate API keys regularly