# 📋 GUVI Hackathon Submission Checklist

## Pre-Submission Checklist

### ✅ Development Phase
- [ ] Installed all dependencies (`pip install -r requirements.txt`)
- [ ] Configured API key in `.env` file
- [ ] Tested locally (`python honeypot_api.py`)
- [ ] Ran quick test (`python test_honeypot.py --quick`)
- [ ] Ran full test suite (`python test_honeypot.py`)
- [ ] Verified all tests pass

### ✅ Deployment Phase
- [ ] Chose deployment platform (Railway/Render/Heroku/Docker)
- [ ] Deployed application successfully
- [ ] Configured environment variables (API_SECRET_KEY)
- [ ] API is publicly accessible
- [ ] Health check works (`GET /health`)

### ✅ Testing Deployed API
- [ ] Tested `/health` endpoint from public URL
- [ ] Tested `/detect` endpoint with sample scam message
- [ ] Verified authentication works (401 without API key)
- [ ] Verified scam detection works
- [ ] Verified agent responses are human-like
- [ ] Verified multi-turn conversation works
- [ ] Verified intelligence extraction works

### ✅ Verification Commands

#### Test Health Endpoint
```bash
curl https://your-api-url.com/health
```
Expected: `{"status":"healthy","service":"Agentic Honey-Pot API"}`

#### Test Detect Endpoint
```bash
curl -X POST https://your-api-url.com/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "sessionId": "verify-001",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Verify immediately.",
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
Expected: `{"status":"success","reply":"<human-like response>"}`

### ✅ Submission Requirements

#### Information to Submit
1. **API Endpoint URL**: 
   ```
   https://your-deployed-api.com/detect
   ```

2. **API Key**: 
   ```
   your-configured-secret-key
   ```

3. **Deployment Platform** (optional but helpful):
   - [ ] Railway
   - [ ] Render
   - [ ] Heroku
   - [ ] Google Cloud Run
   - [ ] AWS
   - [ ] Other: _____________

### ✅ Feature Verification

#### Scam Detection
- [ ] Detects bank fraud messages
- [ ] Detects UPI fraud messages
- [ ] Detects phishing attempts
- [ ] Detects fake offers/lottery
- [ ] Detects impersonation (govt/tax)
- [ ] Detects OTP fraud

#### Agent Behavior
- [ ] Responds with human-like messages
- [ ] Uses appropriate persona based on scam type
- [ ] Asks probing questions
- [ ] Shows concern/interest initially
- [ ] Shows hesitation mid-conversation
- [ ] Concludes conversation appropriately

#### Intelligence Extraction
- [ ] Extracts bank account numbers
- [ ] Extracts UPI IDs
- [ ] Extracts phishing links
- [ ] Extracts phone numbers
- [ ] Extracts suspicious keywords

#### API Functionality
- [ ] Accepts POST requests at `/detect`
- [ ] Requires `x-api-key` header
- [ ] Accepts correct JSON format
- [ ] Returns correct JSON format
- [ ] Handles conversation history
- [ ] Maintains session state

#### Reporting
- [ ] Sends final result to GUVI endpoint after sufficient engagement
- [ ] Includes all required fields in callback
- [ ] Includes extracted intelligence
- [ ] Includes agent notes

### ✅ Performance Checks
- [ ] API responds within 2 seconds
- [ ] Handles multiple concurrent requests
- [ ] No crashes or 500 errors during testing
- [ ] Proper error messages for invalid requests
- [ ] Consistent behavior across multiple tests

### ✅ Security Checks
- [ ] API key authentication works
- [ ] Returns 401 for missing/invalid API key
- [ ] No sensitive data in logs
- [ ] HTTPS enabled (if required by platform)
- [ ] CORS configured if needed

## 🎯 Final Submission

### What Evaluators Will Test

1. **Authentication**
   - Send request without API key → Expect 401
   - Send request with wrong API key → Expect 401
   - Send request with correct API key → Expect 200

2. **Scam Detection**
   - Send various scam messages
   - Verify detection accuracy
   - Check response relevance

3. **Agent Engagement**
   - Test multi-turn conversations (7+ messages)
   - Verify human-like responses
   - Check context awareness

4. **Intelligence Extraction**
   - Send messages with bank accounts → Verify extraction
   - Send messages with UPI IDs → Verify extraction
   - Send messages with links → Verify extraction
   - Send messages with phone numbers → Verify extraction

5. **API Stability**
   - Send rapid sequential requests
   - Send concurrent requests
   - Check response times
   - Verify error handling

6. **Final Callback**
   - Verify callback sent to GUVI endpoint
   - Check payload format
   - Verify intelligence included
   - Check agent notes

### Expected Evaluation Scenarios

#### Scenario 1: Bank Fraud
```
Message: "Your account is blocked. Click here: http://fake-bank.com"
Expected: Detect bank_fraud, extract link, respond with concern
```

#### Scenario 2: UPI Fraud
```
Message: "Send ₹500 to scammer@paytm for verification"
Expected: Detect upi_fraud, extract UPI ID, ask questions
```

#### Scenario 3: Multi-Turn
```
Turn 1: "Urgent: Account issue"
Turn 2: "Share your details"
Turn 3: "Send OTP code"
...
Turn 7+: Agent concludes, sends final callback
```

## 📊 Scoring Criteria (Expected)

| Criterion | Weight | Your Score |
|-----------|--------|------------|
| Scam Detection Accuracy | 20% | ___ / 20 |
| Agent Response Quality | 25% | ___ / 25 |
| Intelligence Extraction | 20% | ___ / 20 |
| API Stability | 15% | ___ / 15 |
| Multi-turn Engagement | 15% | ___ / 15 |
| Ethical Behavior | 5% | ___ / 5 |
| **Total** | **100%** | ___ / 100 |

## 🚨 Common Mistakes to Avoid

- [ ] ❌ Forgetting to set environment variables after deployment
- [ ] ❌ Using HTTP instead of HTTPS for production
- [ ] ❌ Not testing the deployed URL before submission
- [ ] ❌ Hardcoding API keys in the code
- [ ] ❌ Not handling conversation history properly
- [ ] ❌ Sending callback too early (before sufficient engagement)
- [ ] ❌ Not including all required fields in responses
- [ ] ❌ API key visible in public repositories
- [ ] ❌ Deployment sleeping/timing out (free tier issue)

## 📝 Pre-Submission Test Script

Run this to verify everything works:

```bash
# 1. Test health
curl https://your-api.com/health

# 2. Test authentication
curl -X POST https://your-api.com/detect \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test","message":{"sender":"scammer","text":"test","timestamp":123}}'
# Should return 401

# 3. Test scam detection
curl -X POST https://your-api.com/detect \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "sessionId":"test-001",
    "message":{
      "sender":"scammer",
      "text":"Your bank account will be blocked today.",
      "timestamp":1770005528731
    },
    "conversationHistory":[],
    "metadata":{"channel":"SMS","language":"English","locale":"IN"}
  }'
# Should return success with reply

# 4. Run full test suite
python test_honeypot.py
```

## ✅ Ready to Submit?

If you checked all boxes above, you're ready to submit!

### Submit These Details:
1. **API Endpoint**: `https://_____________________.com/detect`
2. **API Key**: `_______________________________________`

### After Submission:
- Keep your API running
- Monitor for any errors
- Don't change API key or URL
- Be available for any clarifications

---

## 🎉 Good Luck!

Your agentic honeypot is ready for evaluation. The system is designed to:
- ✅ Detect scams accurately
- ✅ Engage scammers naturally
- ✅ Extract valuable intelligence
- ✅ Report results automatically

**Trust your implementation and submit with confidence!** 🚀

---

## 📞 Need Help?

### Before Submission:
1. Re-read QUICKSTART.md
2. Check README.md for details
3. Review API_EXAMPLES.md
4. Run test_honeypot.py

### Common Issues Quick Fix:
- **401 Error**: Check API key in headers
- **422 Error**: Verify JSON format
- **500 Error**: Check server logs
- **Timeout**: Increase server resources

---

## 📅 Timeline Checklist

- [ ] **Day 1**: Setup and local testing
- [ ] **Day 2**: Deployment and public testing
- [ ] **Day 3**: Final verification and submission
- [ ] **Evaluation Day**: Keep API running and monitor

---

**You've got this! 💪**