#!/usr/bin/env python3
"""
Quick test to verify MAMA-AI application is working
"""
import requests
import json

def test_endpoints():
    """Test basic application endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing MAMA-AI Application Endpoints")
    print("=" * 50)
    
    # Test home endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Home endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Home endpoint error: {e}")
    
    # Test voice endpoint
    try:
        response = requests.post(f"{base_url}/voice", data={
            'phoneNumber': '+254722123456',
            'sessionId': 'test_session'
        })
        print(f"✅ Voice endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response contains XML: {'<Response>' in response.text}")
    except Exception as e:
        print(f"❌ Voice endpoint error: {e}")
    
    # Test SMS endpoint
    try:
        response = requests.post(f"{base_url}/sms", data={
            'from': '+254722123456',
            'text': 'Hello MAMA-AI',
            'to': '+254727230675'
        })
        print(f"✅ SMS endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ SMS endpoint error: {e}")
    
    # Test USSD endpoint
    try:
        response = requests.post(f"{base_url}/ussd", data={
            'phoneNumber': '+254722123456',
            'text': '',
            'sessionId': 'test_session'
        })
        print(f"✅ USSD endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ USSD endpoint error: {e}")
    
    print("\n🎉 Basic endpoint testing complete!")
    print("\n📋 Next steps:")
    print("1. Configure your Africa's Talking credentials in .env")
    print("2. Set up ngrok public URL in Africa's Talking dashboard")
    print("3. Test with real SMS, USSD, and Voice calls")

if __name__ == "__main__":
    test_endpoints()
