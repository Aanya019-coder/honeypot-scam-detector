#!/usr/bin/env python3
"""
Test script for Agentic Honey-Pot API
Tests various scam scenarios and validates responses
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"  # Change to your deployed URL
API_KEY = "your-secret-api-key-here"  # Change to your actual API key

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def test_health_check():
    """Test health endpoint"""
    print("\n🏥 Testing health check...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_scam_scenario(scenario_name, session_id, messages):
    """Test a complete scam scenario with multiple messages"""
    print(f"\n🎭 Testing {scenario_name}...")
    print("="*60)
    
    conversation_history = []
    
    for i, scam_message in enumerate(messages):
        print(f"\n📨 Message {i+1}/{len(messages)}")
        print(f"Scammer: {scam_message}")
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": scam_message,
                "timestamp": int(datetime.now().timestamp() * 1000)
            },
            "conversationHistory": conversation_history.copy(),
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        try:
            response = requests.post(
                f"{API_URL}/detect",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Agent: {result['reply']}")
                
                # Add to conversation history
                conversation_history.append({
                    "sender": "scammer",
                    "text": scam_message,
                    "timestamp": payload["message"]["timestamp"]
                })
                conversation_history.append({
                    "sender": "user",
                    "text": result['reply'],
                    "timestamp": int(datetime.now().timestamp() * 1000)
                })
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return False
        
        # Small delay between messages
        time.sleep(1)
    
    print(f"\n✅ {scenario_name} completed successfully!")
    return True

def run_all_tests():
    """Run all test scenarios"""
    
    print("\n" + "="*60)
    print("🚀 AGENTIC HONEY-POT API TEST SUITE")
    print("="*60)
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n❌ Health check failed. Please ensure the API is running.")
        return
    
    # Test 2: Bank Fraud Scenario
    test_scam_scenario(
        "Bank Fraud Scenario",
        "test-bank-fraud-001",
        [
            "Your bank account will be blocked today. Verify immediately.",
            "Click this link to verify: http://fake-bank-verify.com/urgent",
            "We need your account number to prevent blocking.",
            "Share your 16-digit account number: XXXX-XXXX-XXXX-XXXX",
            "Also provide your UPI ID for verification.",
            "Final step: Share the OTP sent to your phone.",
            "Thank you. Your account is now safe."
        ]
    )
    
    # Test 3: UPI Fraud Scenario
    test_scam_scenario(
        "UPI Fraud Scenario",
        "test-upi-fraud-002",
        [
            "Your UPI payment of ₹5000 is pending. Confirm to receive refund.",
            "Share your UPI ID to process the refund immediately.",
            "We will send ₹5000 to your scammer@paytm account.",
            "Please confirm your phone number +919876543210 for verification.",
            "Click here to complete: www.fake-upi-refund.in/claim"
        ]
    )
    
    # Test 4: Phishing Scenario
    test_scam_scenario(
        "Phishing Scenario",
        "test-phishing-003",
        [
            "URGENT: Update your KYC details to avoid account suspension.",
            "Download our official app from: http://malicious-app-download.xyz",
            "Install the security certificate for verification.",
            "Login with your internet banking credentials to proceed.",
            "Enter your debit card number and CVV for final verification."
        ]
    )
    
    # Test 5: Fake Lottery Scenario
    test_scam_scenario(
        "Fake Lottery Scenario",
        "test-lottery-004",
        [
            "Congratulations! You have won ₹10 Lakhs in the national lottery!",
            "Claim your prize money before it expires in 24 hours!",
            "Pay processing fee of ₹5000 to claim your prize.",
            "Send money to UPI: winner@okaxis or Account: 1234567890123456",
            "Limited time offer - Act now to receive your prize!"
        ]
    )
    
    # Test 6: Impersonation Scenario
    test_scam_scenario(
        "Government Impersonation Scenario",
        "test-impersonation-005",
        [
            "Income Tax Department Notice: You have pending tax arrears.",
            "Legal action will be initiated if payment not received today.",
            "Pay penalty amount immediately to avoid arrest warrant.",
            "Call our officer at +911234567890 for clearance.",
            "Failure to comply will result in account freeze and prosecution."
        ]
    )
    
    # Test 7: OTP Fraud Scenario
    test_scam_scenario(
        "OTP Fraud Scenario",
        "test-otp-fraud-006",
        [
            "We have detected suspicious activity on your account.",
            "An OTP has been sent to your registered mobile number.",
            "Share the 6-digit code to verify it's really you.",
            "The code will expire in 5 minutes. Please hurry!",
            "Also confirm your account number for security purposes."
        ]
    )
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
    print("\n📊 Summary:")
    print("- Health check: Passed")
    print("- Bank fraud detection: Tested")
    print("- UPI fraud detection: Tested")
    print("- Phishing detection: Tested")
    print("- Fake offer detection: Tested")
    print("- Impersonation detection: Tested")
    print("- OTP fraud detection: Tested")
    print("\n💡 Check your server logs for intelligence extraction results")
    print("💡 Final results should be sent to GUVI callback endpoint")

def test_single_message():
    """Quick test with a single message"""
    print("\n🚀 Quick Single Message Test")
    print("="*60)
    
    payload = {
        "sessionId": "quick-test-999",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately at http://fake-site.com",
            "timestamp": int(datetime.now().timestamp() * 1000)
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    print(f"\n📨 Sending: {payload['message']['text']}")
    
    try:
        response = requests.post(
            f"{API_URL}/detect",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Test passed!")
        else:
            print("\n❌ Test failed!")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        test_single_message()
    else:
        run_all_tests()
    
    print("\n" + "="*60)
    print("Test script completed!")
    print("="*60 + "\n")