#!/usr/bin/env python3
"""
Test script to verify SMS AI functionality
This simulates receiving SMS messages and checks AI responses
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.sms_service import SMSService
from src.models import db, User
from flask import Flask
import tempfile

def create_test_app():
    """Create a test Flask app with in-memory database"""
    app = Flask(__name__)
    
    # Use SQLite in-memory database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    return app

def test_sms_responses():
    """Test various SMS scenarios with AI responses"""
    
    print("🧪 Testing SMS AI Service...")
    print("=" * 50)
    
    # Create test app and SMS service
    app = create_test_app()
    
    with app.app_context():
        sms_service = SMSService()
        
        # Test scenarios
        test_cases = [
            {
                "name": "First-time user greeting",
                "from_number": "+254712345678",
                "text": "START",
                "expected_ai": True
            },
            {
                "name": "Health question about pregnancy",
                "from_number": "+254712345678", 
                "text": "I'm 20 weeks pregnant and having morning sickness. What should I do?",
                "expected_ai": True
            },
            {
                "name": "Help request",
                "from_number": "+254712345678",
                "text": "HELP",
                "expected_ai": True
            },
            {
                "name": "General health question",
                "from_number": "+254712345678",
                "text": "What foods are good during pregnancy?",
                "expected_ai": True
            },
            {
                "name": "Different user - first contact",
                "from_number": "+254787654321",
                "text": "Hi, I need help with my baby",
                "expected_ai": True
            },
            {
                "name": "Unsubscribe request",
                "from_number": "+254712345678",
                "text": "STOP",
                "expected_ai": True  # AI should handle this too
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📱 Test {i}: {test_case['name']}")
            print(f"From: {test_case['from_number']}")
            print(f"Message: {test_case['text']}")
            print("-" * 30)
            
            try:
                # Test the SMS processing (without actually sending)
                user = sms_service._get_or_create_user(test_case['from_number'])
                response = sms_service._process_sms_with_ai(test_case['text'], user)
                
                if response:
                    print(f"✅ AI Response: {response}")
                    print(f"📊 Response length: {len(response)} characters")
                    
                    # Check if response looks AI-generated (not hardcoded)
                    if test_case['expected_ai']:
                        # Look for signs of AI response vs hardcoded
                        ai_indicators = ['mama-ai', 'health', 'pregnancy', 'baby', 'help']
                        has_ai_content = any(indicator.lower() in response.lower() for indicator in ai_indicators)
                        
                        if has_ai_content or len(response) > 50:  # AI responses tend to be longer
                            print("✅ Response appears to be AI-generated")
                        else:
                            print("⚠️  Response might be hardcoded")
                    
                else:
                    print("❌ No response generated")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        print("\n" + "=" * 50)
        print("📈 SMS AI Test Summary:")
        print("- All messages should be processed by AI")
        print("- No hardcoded responses should appear")
        print("- Responses should be contextual and helpful")
        print("- SMS responses should be under 160 chars when possible")

def test_sms_service_config():
    """Test SMS service configuration"""
    print("\n🔧 Testing SMS Service Configuration...")
    print("-" * 40)
    
    try:
        sms_service = SMSService()
        
        print(f"✅ Shortcode: {sms_service.shortcode}")
        print(f"✅ AI Service initialized: {sms_service.ai_service is not None}")
        
        # Test phone number cleaning
        test_numbers = [
            "+254712345678",
            "0712345678", 
            "712345678",
            "254712345678"
        ]
        
        print("\n📞 Phone number cleaning test:")
        for number in test_numbers:
            clean = sms_service._clean_phone_number(number)
            print(f"  {number} → {clean}")
            
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")

if __name__ == "__main__":
    print("🤖 MAMA-AI SMS Service Test")
    print("Testing AI-powered SMS responses with shortcode 15629")
    print("=" * 60)
    
    # Test configuration first
    test_sms_service_config()
    
    # Test AI responses
    test_sms_responses()
    
    print("\n🎯 Test completed!")
    print("💡 Note: This test uses in-memory database and doesn't send actual SMS")
    print("📱 For full testing, send SMS to shortcode 15629 in Africa's Talking sandbox")
