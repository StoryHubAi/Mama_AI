#!/usr/bin/env python3
"""
SMS Test with Different SSL and Environment Settings
"""
import os
import ssl
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_direct_api_call():
    """Test direct API call to Africa's Talking"""
    try:
        # Direct API call using requests
        url = "https://api.sandbox.africastalking.com/version1/messaging"
        
        username = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
        api_key = os.getenv('AFRICASTALKING_API_KEY')
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'apiKey': api_key
        }
        
        data = {
            'username': username,
            'to': '+254712345678',
            'message': 'MAMA-AI Test: Direct API call test! 🤱',
            'from': '15629'
        }
        
        print(f"🔄 Making direct API call...")
        print(f"   URL: {url}")
        print(f"   Username: {username}")
        print(f"   API Key: {api_key[:20]}...")
        
        # Try with SSL verification disabled
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ Direct API call successful!")
            return True
        else:
            print("❌ Direct API call failed")
            return False
            
    except Exception as e:
        print(f"❌ Direct API test failed: {str(e)}")
        return False

def test_sms_via_simulator():
    """Instructions for testing via simulator"""
    print("\n" + "="*60)
    print("📱 ALTERNATIVE: Test via Africa's Talking Simulator")
    print("="*60)
    print("Since the SSL issue is preventing direct SMS sending,")
    print("you can test the SMS functionality via the simulator:")
    print()
    print("1. 🌐 Open: https://sandbox.africastalking.com/")
    print("2. 📱 Go to 'Launch Simulator'")
    print("3. 📝 Send SMS TO shortcode 15629")
    print("4. 💬 Try messages like:")
    print("   - 'hello'")
    print("   - 'help'") 
    print("   - 'pregnancy advice'")
    print("   - 'what should I eat while pregnant?'")
    print()
    print("✅ Your webhook should receive these and AI will respond!")
    print("📍 Webhook URL: Your VS Code tunnel or ngrok URL + /sms")

if __name__ == "__main__":
    print("🧪 Testing SMS Sending...")
    result = test_direct_api_call()
    if not result:
        test_sms_via_simulator()
