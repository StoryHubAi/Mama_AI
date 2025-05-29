#!/usr/bin/env python3
"""
MAMA-AI System Test
Tests SMS and USSD functionality after system startup
"""

import requests
import json
from datetime import datetime

def test_sms_endpoint():
    """Test SMS webhook endpoint"""
    print("📱 Testing SMS Endpoint...")
    
    # Test SMS message
    sms_data = {
        'to': '15629',
        'from': '+254700123456',
        'text': 'Hello MAMA-AI, I am pregnant and need help',
        'date': datetime.now().isoformat(),
        'id': 'test_msg_001',
        'linkId': 'test_link_001'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/sms',
            data=sms_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ SMS endpoint working")
            print(f"   Response: {response.text}")
        else:
            print(f"❌ SMS endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Is it running on port 5000?")
    except Exception as e:
        print(f"❌ SMS test error: {e}")

def test_ussd_endpoint():
    """Test USSD webhook endpoint"""
    print("\n📞 Testing USSD Endpoint...")
    
    # Test USSD main menu
    ussd_data = {
        'sessionId': 'test_session_001',
        'serviceCode': '*123#',
        'phoneNumber': '+254700123456',
        'text': ''
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/ussd',
            data=ussd_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ USSD endpoint working")
            print(f"   Response: {response.text}")
        else:
            print(f"❌ USSD endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Is it running on port 5000?")
    except Exception as e:
        print(f"❌ USSD test error: {e}")

def test_ai_chat_endpoint():
    """Test AI chat endpoint"""
    print("\n🤖 Testing AI Chat Endpoint...")
    
    chat_data = {
        'message': 'What foods should I eat during pregnancy?',
        'phone_number': '+254700123456',
        'language': 'en'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/chat',
            json=chat_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ AI Chat endpoint working")
            result = response.json()
            print(f"   AI Response: {result.get('response', 'No response')[:100]}...")
        else:
            print(f"❌ AI Chat endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Is it running on port 5000?")
    except Exception as e:
        print(f"❌ AI Chat test error: {e}")

def test_health_endpoint():
    """Test health check endpoint"""
    print("\n❤️ Testing Health Check Endpoint...")
    
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        
        if response.status_code == 200:
            print("✅ Health endpoint working")
            result = response.json()
            print(f"   Status: {result}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Is it running on port 5000?")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def main():
    """Run all tests"""
    print("🧪 MAMA-AI System Testing")
    print("=" * 40)
    print("Make sure the Flask app is running on port 5000")
    print("=" * 40)
    
    # Run tests
    test_health_endpoint()
    test_sms_endpoint()
    test_ussd_endpoint()
    test_ai_chat_endpoint()
    
    print("\n" + "=" * 40)
    print("✅ System testing completed!")
    print("\nNext steps:")
    print("1. Configure Africa's Talking webhook URLs")
    print("2. Test with real SMS/USSD from mobile phone")
    print("3. Monitor logs for any issues")

if __name__ == "__main__":
    main()
