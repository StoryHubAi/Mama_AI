#!/usr/bin/env python3
"""
Quick SMS Service Test
Tests if SMS service can be initialized and is ready to send messages
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_sms_service():
    """Test SMS service initialization"""
    try:
        from src.services.sms_service import SMSService
        
        print("🧪 Testing SMS Service...")
        print("=" * 50)
        
        # Initialize SMS service
        sms_service = SMSService()
        
        print(f"📱 Shortcode configured: {sms_service.shortcode}")
        
        # Test phone number cleaning
        test_numbers = [
            "+254722123456",
            "0722123456", 
            "722123456"
        ]
        
        print("\n📋 Testing phone number cleaning:")
        for number in test_numbers:
            clean = sms_service._clean_phone_number(number)
            print(f"   {number} → {clean}")
        
        print("\n✅ SMS Service test completed successfully!")
        print("🔑 Using API key from .env file")
        print(f"🏷️ Shortcode: {sms_service.shortcode}")
        
        return True
        
    except Exception as e:
        print(f"❌ SMS Service test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_sms_service()
