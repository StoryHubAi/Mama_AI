import requests
import json

def test_sms_endpoint():
    """Test the SMS webhook endpoint"""
    
    # Test data simulating Africa's Talking SMS webhook
    test_data = {
        'from': '+254712345678',
        'to': '15629',
        'text': 'Hello, I need help with my pregnancy',
        'date': '2025-05-29 10:30:00'
    }
    
    try:
        print("🧪 Testing SMS endpoint...")
        print(f"📱 Simulating SMS from {test_data['from']}")
        print(f"💬 Message: {test_data['text']}")
        print("-" * 40)
        
        # Send POST request to SMS endpoint
        response = requests.post(
            'http://127.0.0.1:5000/sms',
            data=test_data,
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📊 Response: {response.json()}")
        
        if response.status_code == 200:
            print("🎉 SMS endpoint is working!")
            print("✅ AI should have processed the message and sent a response")
        else:
            print("❌ SMS endpoint error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app")
        print("💡 Make sure the app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error testing SMS endpoint: {str(e)}")

def test_sms_test_endpoint():
    """Test the test-sms endpoint for sending SMS"""
    
    test_data = {
        'phone_number': '+254712345678',
        'message': 'Test message from MAMA-AI! 🤱'
    }
    
    try:
        print("\n🧪 Testing SMS sending endpoint...")
        print(f"📱 Sending test SMS to {test_data['phone_number']}")
        print(f"💬 Message: {test_data['message']}")
        print("-" * 40)
        
        # Send POST request to test-sms endpoint
        response = requests.post(
            'http://127.0.0.1:5000/test-sms',
            json=test_data,
            timeout=30
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📊 Response: {response.json()}")
        
        if response.status_code == 200:
            print("🎉 SMS sending endpoint is working!")
        else:
            print("❌ SMS sending endpoint error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app")
    except Exception as e:
        print(f"❌ Error testing SMS sending: {str(e)}")

if __name__ == "__main__":
    print("📱 MAMA-AI SMS Endpoint Test")
    print("=" * 40)
    
    # Test receiving SMS (webhook)
    test_sms_endpoint()
    
    # Test sending SMS
    test_sms_test_endpoint()
    
    print("\n✨ Test completed!")
    print("💡 Check the Flask app console for detailed logs")
