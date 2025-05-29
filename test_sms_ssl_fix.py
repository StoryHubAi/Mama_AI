#!/usr/bin/env python3
"""
SMS SSL Fix Test
Tests sending SMS with SSL configuration fixes
"""
import os
import ssl
import africastalking
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sms_with_ssl_fix():
    """Test SMS sending with SSL configuration"""
    try:
        # Disable SSL verification for sandbox (temporary fix)
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Initialize Africa's Talking
        username = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
        api_key = os.getenv('AFRICASTALKING_API_KEY')
        
        print(f"🔑 Testing with API Key: {api_key[:20]}...")
        
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS
        
        # Test message
        test_message = "MAMA-AI Test: Hello from your maternal health assistant! 🤱"
        test_phone = "+254712345678"  # Your test number
        shortcode = "15629"
        
        print(f"📤 Sending test SMS...")
        print(f"   To: {test_phone}")
        print(f"   Message: {test_message}")
        print(f"   From: {shortcode}")
        
        # Try different SMS formats
        try:
            # Format 1: Named parameters
            response = sms.send(
                message=test_message,
                recipients=[test_phone],
                sender_id=shortcode
            )
            print(f"✅ SMS sent successfully!")
            print(f"📊 Response: {response}")
            
        except Exception as e1:
            print(f"❌ Format 1 failed: {e1}")
            try:
                # Format 2: Positional parameters
                response = sms.send(test_message, [test_phone], shortcode)
                print(f"✅ SMS sent successfully with Format 2!")
                print(f"📊 Response: {response}")
                
            except Exception as e2:
                print(f"❌ Format 2 also failed: {e2}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_sms_with_ssl_fix()
