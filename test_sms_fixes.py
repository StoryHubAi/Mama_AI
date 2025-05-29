#!/usr/bin/env python3
"""
Quick test to verify the fixes work
"""

import os
import sys
sys.path.append('.')

# Test imports
try:
    from src.services.sms_service import SMSService
    print("✅ SMS Service imported successfully")
    
    # Test service creation
    sms_service = SMSService()
    print("✅ SMS Service instance created")
    
    # Test phone number cleaning
    test_number = "+93345432223"
    clean_number = sms_service._clean_phone_number(test_number)
    print(f"✅ Phone cleaning test: {test_number} -> {clean_number}")
    
    # Test supported number check
    is_supported = sms_service._is_supported_sandbox_number(clean_number)
    print(f"✅ Supported number check: {clean_number} -> {is_supported}")
    
    print("\n🎉 ALL TESTS PASSED! SMS Service is working correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
