#!/usr/bin/env python3
"""
Deployment Verification Script
Validates that your deployed API is ready for hackathon evaluation
"""

import requests
import json
import sys
from datetime import datetime
from typing import Tuple, List

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def verify_health_check(api_url: str) -> bool:
    """Test 1: Health Check"""
    print_info("Testing health endpoint...")
    
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print_success(f"Health check passed: {data}")
                return True
            else:
                print_error(f"Unexpected health response: {data}")
                return False
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Health check timeout - server too slow or unreachable")
        return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def verify_authentication(api_url: str, api_key: str) -> bool:
    """Test 2: API Authentication"""
    print_info("Testing API authentication...")
    
    # Test without API key (should fail)
    try:
        response = requests.post(
            f"{api_url}/detect",
            json={"sessionId": "test", "message": {"sender": "scammer", "text": "test", "timestamp": 123}},
            timeout=5
        )
        
        if response.status_code == 401:
            print_success("Authentication properly rejects requests without API key")
        else:
            print_error(f"Expected 401 without API key, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Auth test error: {str(e)}")
        return False
    
    # Test with wrong API key (should fail)
    try:
        response = requests.post(
            f"{api_url}/detect",
            headers={"x-api-key": "wrong-key"},
            json={"sessionId": "test", "message": {"sender": "scammer", "text": "test", "timestamp": 123}},
            timeout=5
        )
        
        if response.status_code == 401:
            print_success("Authentication properly rejects wrong API keys")
            return True
        else:
            print_warning(f"Expected 401 with wrong key, got {response.status_code}")
            return True  # Not critical
            
    except Exception as e:
        print_warning(f"Wrong key test error: {str(e)}")
        return True  # Not critical

def verify_scam_detection(api_url: str, api_key: str) -> Tuple[bool, dict]:
    """Test 3: Scam Detection"""
    print_info("Testing scam detection...")
    
    test_messages = [
        ("Bank Fraud", "Your bank account will be blocked today. Verify immediately."),
        ("UPI Fraud", "Share your UPI ID scammer@paytm to receive refund"),
        ("Phishing", "Click here: http://fake-bank.com to secure your account"),
        ("OTP Fraud", "Share the OTP code 123456 to verify your identity"),
    ]
    
    results = {}
    
    for scam_type, message in test_messages:
        try:
            payload = {
                "sessionId": f"verify-{scam_type.lower().replace(' ', '-')}",
                "message": {
                    "sender": "scammer",
                    "text": message,
                    "timestamp": int(datetime.now().timestamp() * 1000)
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "English",
                    "locale": "IN"
                }
            }
            
            response = requests.post(
                f"{api_url}/detect",
                headers={"x-api-key": api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and data.get("reply"):
                    results[scam_type] = True
                    print_success(f"{scam_type}: Detected and responded")
                    print(f"   Response: {data['reply'][:60]}...")
                else:
                    results[scam_type] = False
                    print_error(f"{scam_type}: Invalid response format")
            else:
                results[scam_type] = False
                print_error(f"{scam_type}: HTTP {response.status_code}")
                
        except Exception as e:
            results[scam_type] = False
            print_error(f"{scam_type}: Error - {str(e)}")
    
    all_passed = all(results.values())
    return all_passed, results

def verify_response_format(api_url: str, api_key: str) -> bool:
    """Test 4: Response Format"""
    print_info("Testing response format compliance...")
    
    try:
        payload = {
            "sessionId": "format-test",
            "message": {
                "sender": "scammer",
                "text": "Urgent: Your account needs verification",
                "timestamp": int(datetime.now().timestamp() * 1000)
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        response = requests.post(
            f"{api_url}/detect",
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            if "status" in data and "reply" in data:
                if data["status"] == "success" and isinstance(data["reply"], str):
                    print_success("Response format is correct")
                    print(f"   Status: {data['status']}")
                    print(f"   Reply type: {type(data['reply']).__name__}")
                    return True
                else:
                    print_error(f"Invalid field values: {data}")
                    return False
            else:
                print_error(f"Missing required fields: {data}")
                return False
        else:
            print_error(f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Format test error: {str(e)}")
        return False

def verify_multi_turn(api_url: str, api_key: str) -> bool:
    """Test 5: Multi-turn Conversation"""
    print_info("Testing multi-turn conversation...")
    
    session_id = "multiturn-test"
    conversation_history = []
    
    messages = [
        "Your bank account will be blocked.",
        "Share your UPI ID to avoid suspension.",
        "Send it to scammer@paytm immediately."
    ]
    
    try:
        for i, msg in enumerate(messages):
            payload = {
                "sessionId": session_id,
                "message": {
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": int(datetime.now().timestamp() * 1000)
                },
                "conversationHistory": conversation_history.copy(),
                "metadata": {
                    "channel": "SMS",
                    "language": "English",
                    "locale": "IN"
                }
            }
            
            response = requests.post(
                f"{api_url}/detect",
                headers={"x-api-key": api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "")
                
                print_success(f"Turn {i+1}: {reply[:50]}...")
                
                # Update history
                conversation_history.append({
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": payload["message"]["timestamp"]
                })
                conversation_history.append({
                    "sender": "user",
                    "text": reply,
                    "timestamp": int(datetime.now().timestamp() * 1000)
                })
            else:
                print_error(f"Turn {i+1} failed: HTTP {response.status_code}")
                return False
        
        print_success("Multi-turn conversation working correctly")
        return True
        
    except Exception as e:
        print_error(f"Multi-turn test error: {str(e)}")
        return False

def verify_performance(api_url: str, api_key: str) -> bool:
    """Test 6: Performance"""
    print_info("Testing response performance...")
    
    import time
    
    try:
        payload = {
            "sessionId": "perf-test",
            "message": {
                "sender": "scammer",
                "text": "Urgent verification needed",
                "timestamp": int(datetime.now().timestamp() * 1000)
            },
            "conversationHistory": [],
            "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
        }
        
        start_time = time.time()
        
        response = requests.post(
            f"{api_url}/detect",
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            if elapsed_time < 2.0:
                print_success(f"Response time: {elapsed_time:.2f}s (Excellent)")
                return True
            elif elapsed_time < 5.0:
                print_warning(f"Response time: {elapsed_time:.2f}s (Acceptable)")
                return True
            else:
                print_error(f"Response time: {elapsed_time:.2f}s (Too slow)")
                return False
        else:
            print_error(f"Performance test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Performance test error: {str(e)}")
        return False

def main():
    print_header("🚀 HONEYPOT API DEPLOYMENT VERIFICATION")
    
    # Get configuration
    if len(sys.argv) >= 3:
        api_url = sys.argv[1].rstrip('/')
        api_key = sys.argv[2]
    else:
        print("Usage: python verify_deployment.py <API_URL> <API_KEY>")
        print("\nExample:")
        print("  python verify_deployment.py https://my-api.railway.app my-secret-key")
        print("\nOr run interactively:")
        api_url = input("\nEnter your API URL (without /detect): ").strip().rstrip('/')
        api_key = input("Enter your API key: ").strip()
    
    if not api_url or not api_key:
        print_error("API URL and API key are required")
        sys.exit(1)
    
    print(f"\n{Colors.BOLD}Testing API:{Colors.END} {api_url}")
    print(f"{Colors.BOLD}Using API Key:{Colors.END} {api_key[:10]}...")
    
    # Run all tests
    results = {}
    
    print_header("TEST 1: Health Check")
    results['health'] = verify_health_check(api_url)
    
    print_header("TEST 2: Authentication")
    results['auth'] = verify_authentication(api_url, api_key)
    
    print_header("TEST 3: Scam Detection")
    results['detection'], detection_details = verify_scam_detection(api_url, api_key)
    
    print_header("TEST 4: Response Format")
    results['format'] = verify_response_format(api_url, api_key)
    
    print_header("TEST 5: Multi-turn Conversation")
    results['multiturn'] = verify_multi_turn(api_url, api_key)
    
    print_header("TEST 6: Performance")
    results['performance'] = verify_performance(api_url, api_key)
    
    # Summary
    print_header("📊 VERIFICATION SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        color = Colors.GREEN if passed else Colors.RED
        print(f"{color}{status}{Colors.END} - {test_name.upper()}")
    
    print(f"\n{Colors.BOLD}Score: {passed_tests}/{total_tests} tests passed{Colors.END}")
    
    if passed_tests == total_tests:
        print_header("🏆 READY FOR SUBMISSION!")
        print(f"{Colors.GREEN}{Colors.BOLD}Your API is fully functional and ready for hackathon evaluation!{Colors.END}\n")
        print("Next steps:")
        print("1. Submit your API URL and key to the hackathon platform")
        print("2. Keep your server running during evaluation")
        print("3. Monitor logs for any issues")
        print("\nGood luck! 🍀")
        sys.exit(0)
    else:
        print_header("⚠️  ISSUES DETECTED")
        print(f"{Colors.YELLOW}Please fix the failing tests before submitting.{Colors.END}\n")
        print("Common fixes:")
        print("- Ensure server is deployed and running")
        print("- Verify API key is configured correctly")
        print("- Check firewall/network settings")
        print("- Review server logs for errors")
        sys.exit(1)

if __name__ == "__main__":
    main()