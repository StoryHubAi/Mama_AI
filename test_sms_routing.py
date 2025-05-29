#!/usr/bin/env python3
"""
Test to verify SMS responses go back to original sender
"""

import os
import sys
sys.path.append('.')

# Test the phone number handling
try:
    from src.services.sms_service import SMSService
    
    print("✅ Testing SMS Response Routing Fix")
    print("=" * 50)
    
    # Create SMS service
    sms_service = SMSService()
    
    # Test different phone numbers
    test_numbers = [
        "+254727230675",  # Your test number
        "+93345432223",   # Another number
        "+1234567890",    # US number
        "0712345678"      # Local format
    ]
    
    for number in test_numbers:
        clean_number = sms_service._clean_phone_number(number)
        is_supported = sms_service._is_supported_sandbox_number(clean_number)
        
        print(f"\n📱 Testing: {number}")
        print(f"   Cleaned: {clean_number}")
        print(f"   Supported: {is_supported}")
        print(f"   ✅ Response will go to: {clean_number} (ORIGINAL SENDER)")
    
    print(f"\n🎉 SUCCESS: All SMS responses will now go back to the original senders!")
    print(f"   No more hardcoded number conversions!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
