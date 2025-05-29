#!/usr/bin/env python3
"""
Quick test to send SMS directly using Africa's Talking
"""
import os
from dotenv import load_dotenv
import africastalking

# Load environment variables
load_dotenv()

# Fix SSL issues for Africa's Talking sandbox - COMPREHENSIVE FIX
import ssl
import urllib3

# Create unverified SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Additional SSL bypass for requests library
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create a custom session with SSL disabled
session = requests.Session()
session.verify = False

# Monkey patch the africastalking library to use our session
import africastalking.Service as ATService
if hasattr(ATService, 'Service'):
    original_post = ATService.Service._make_request
    
    def patched_post(self, url, data, headers):
        """Patched request method with SSL disabled"""
        try:
            response = session.post(url, data=data, headers=headers, verify=False, timeout=30)
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            raise
    
    ATService.Service._make_request = patched_post

def test_direct_sms():
    """Test direct SMS sending"""
    try:
        # Initialize Africa's Talking
        username = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
        api_key = os.getenv('AFRICASTALKING_API_KEY')
        shortcode = os.getenv('AFRICASTALKING_SHORTCODE', '15629')
        
        print(f"🔑 Testing with:")
        print(f"   Username: {username}")
        print(f"   API Key: {api_key[:20]}..." if api_key else "   API Key: None")
        print(f"   Shortcode: {shortcode}")
        
        if not api_key:
            print("❌ No API key found!")
            return False
            
        # Initialize
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS
        
        # Test message
        phone_number = "+93345432223"  # From your logs
        message = "Hello! This is a test message from MAMA-AI. 🤖"
        
        print(f"\n📱 SENDING TEST SMS:")
        print(f"   To: {phone_number}")
        print(f"   Message: {message}")
        print(f"   From: {shortcode}")
        
        # Send SMS - try both formats
        print("\n🔄 Method 1: With sender_id...")
        try:
            response1 = sms.send(
                message=message,
                recipients=[phone_number],
                sender_id=shortcode
            )
            print(f"✅ Method 1 Success: {response1}")
            return True
        except Exception as e1:
            print(f"❌ Method 1 Failed: {e1}")
            
        print("\n🔄 Method 2: Without sender_id...")
        try:
            response2 = sms.send(message, [phone_number])
            print(f"✅ Method 2 Success: {response2}")
            return True
        except Exception as e2:
            print(f"❌ Method 2 Failed: {e2}")
            
        print("\n🔄 Method 3: Simple format...")
        try:
            response3 = sms.send(
                message=message,
                recipients=[phone_number]
            )
            print(f"✅ Method 3 Success: {response3}")
            return True
        except Exception as e3:
            print(f"❌ Method 3 Failed: {e3}")
            
        return False
        
    except Exception as e:
        print(f"❌ Direct SMS test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing direct SMS sending...")
    success = test_direct_sms()
    
    if success:
        print("\n✅ SMS sending works! Check Africa's Talking Simulator")
    else:
        print("\n❌ SMS sending failed - check credentials and configuration")
