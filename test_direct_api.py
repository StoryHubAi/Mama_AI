#!/usr/bin/env python3
"""
Simple SMS test with direct requests to Africa's Talking API
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_direct_api_call():
    """Test direct API call to Africa's Talking"""
    try:
        username = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
        api_key = os.getenv('AFRICASTALKING_API_KEY')
        shortcode = os.getenv('AFRICASTALKING_SHORTCODE', '15629')
        
        if not api_key:
            print("❌ No API key found!")
            return False
            
        # Africa's Talking API endpoint for sandbox
        url = "https://api.sandbox.africastalking.com/version1/messaging"
        
        # Headers
        headers = {
            'apikey': api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
          # Test with multiple phone numbers (sandbox test numbers)
        test_numbers = [
            '+254712345678',  # Kenya test number
            '+256712345678',  # Uganda test number  
            '+255712345678',  # Tanzania test number
            '+93345432223'    # Your original number
        ]
        
        for phone_number in test_numbers:
            print(f"\n📱 TESTING PHONE NUMBER: {phone_number}")
            
            # Data
            data = {
                'username': username,
                'to': phone_number,
                'message': f'Hello from MAMA-AI! Test for {phone_number} 🤖'
            }
            
            # Make request with SSL verification disabled
            response = requests.post(
                url, 
                headers=headers, 
                data=data, 
                verify=False,  # Disable SSL verification
                timeout=30
            )
            
            print(f"📊 Status: {response.status_code}")
            print(f"📊 Response: {response.text}")
            
            if response.status_code == 201 and "UnsupportedNumberType" not in response.text:
                print(f"✅ SUCCESS with {phone_number}!")
                return True
            
    except Exception as e:
        print(f"❌ Direct API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing direct Africa's Talking API call...")
    success = test_direct_api_call()
    
    if success:
        print("\n✅ Direct API works! SMS should appear in simulator")
    else:
        print("\n❌ Direct API failed - check credentials")
