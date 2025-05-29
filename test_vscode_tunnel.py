"""
🧪 Testing MAMA-AI SMS with VS Code Port Forwarding
==================================================

Your SMS webhook URL: https://k99gkq4s-5000.euw.devtunnels.ms/sms
Your delivery report URL: https://k99gkq4s-5000.euw.devtunnels.ms/delivery-report

Let's test this immediately!
"""

import requests
import json
import time

def test_webhook_directly():
    """Test the SMS webhook directly using your VS Code tunnel"""
    
    webhook_url = "https://k99gkq4s-5000.euw.devtunnels.ms/sms"
    
    print("🚀 Testing MAMA-AI SMS with VS Code Port Forwarding")
    print("=" * 60)
    print(f"📡 Webhook URL: {webhook_url}")
    print()
    
    # Test cases simulating Africa's Talking SMS webhook
    test_cases = [
        {
            "name": "First Contact - START",
            "data": {
                "from": "+254712345678",
                "to": "15629", 
                "text": "START",
                "date": "2025-05-29 10:30:00"
            }
        },
        {
            "name": "Health Question - Pregnancy",
            "data": {
                "from": "+254712345678",
                "to": "15629",
                "text": "I'm 20 weeks pregnant and having morning sickness. What should I do?",
                "date": "2025-05-29 10:31:00"
            }
        },
        {
            "name": "Help Request",
            "data": {
                "from": "+254712345678", 
                "to": "15629",
                "text": "HELP",
                "date": "2025-05-29 10:32:00"
            }
        },
        {
            "name": "Different User - Baby Question",
            "data": {
                "from": "+254787654321",
                "to": "15629",
                "text": "My 3 month old baby won't stop crying, what should I do?",
                "date": "2025-05-29 10:33:00"
            }
        },
        {
            "name": "General Health",
            "data": {
                "from": "+254712345678",
                "to": "15629", 
                "text": "What foods are good during pregnancy?",
                "date": "2025-05-29 10:34:00"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📱 Test {i}: {test_case['name']}")
        print(f"From: {test_case['data']['from']}")
        print(f"Message: {test_case['data']['text']}")
        print("-" * 50)
        
        try:
            # Send POST request to your SMS webhook
            response = requests.post(
                webhook_url,
                data=test_case['data'],
                timeout=30,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            print(f"✅ Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"📊 Response: {result}")
                print("🎉 SMS processed successfully!")
                print("💡 Check your Flask console for AI response details")
            else:
                print(f"❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {str(e)}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            
        print()
        time.sleep(2)  # Small delay between tests
    
    print("=" * 60)
    print("🎯 Testing Complete!")
    print()
    print("✅ If you see 'SMS processed successfully' messages above,")
    print("   your SMS service is working perfectly!")
    print()
    print("📱 Next Steps:")
    print("1. Go to Africa's Talking dashboard")
    print("2. Set SMS Callback URL to:")
    print("   https://k99gkq4s-5000.euw.devtunnels.ms/sms")
    print("3. Set Delivery Report URL to:")
    print("   https://k99gkq4s-5000.euw.devtunnels.ms/delivery-report")
    print("4. Test with real SMS in simulator!")

def test_webhook_accessibility():
    """Test if the webhook URL is accessible"""
    print("🔍 Testing Webhook Accessibility")
    print("-" * 40)
    
    base_url = "https://k99gkq4s-5000.euw.devtunnels.ms"
    
    # Test if the base URL is accessible
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"✅ Base URL accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Base URL error: {str(e)}")
        return False
    
    # Test if SMS endpoint exists
    try:
        # Send a GET to SMS endpoint (should return 405 Method Not Allowed)
        response = requests.get(f"{base_url}/sms", timeout=10)
        if response.status_code == 405:
            print("✅ SMS endpoint exists (expects POST)")
        else:
            print(f"⚠️  SMS endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"❌ SMS endpoint error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    # First check if webhook is accessible
    if test_webhook_accessibility():
        print()
        # Then test SMS processing
        test_webhook_directly()
    else:
        print("❌ Webhook not accessible. Make sure:")
        print("1. Flask app is running")
        print("2. VS Code port forwarding is active")
        print("3. Port 5000 is forwarded correctly")
