#!/usr/bin/env python3
"""
MAMA-AI Integration Test Script
Tests AI functionality, SMS, and USSD integration
"""

import os
import sys
import requests
import json
from datetime import datetime

# Test configuration
FLASK_APP_URL = "http://localhost:5000"
TEST_PHONE = "+254700123456"

def test_ai_chat():
    """Test AI chat functionality"""
    print("🤖 Testing AI Chat Integration...")
    
    test_messages = [
        "Nina maumivu ya tumbo",  # Swahili symptoms
        "I have a headache",      # English symptoms  
        "When is my next appointment?",  # Appointment query
        "Heavy bleeding",         # Emergency case
        "I feel tired",          # Normal pregnancy symptom
        "What should I eat during pregnancy?"  # Nutrition question
    ]
    
    for message in test_messages:
        try:
            payload = {
                "message": message,
                "phone_number": TEST_PHONE
            }
            
            response = requests.post(
                f"{FLASK_APP_URL}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Message: '{message[:30]}...'")
                print(f"   AI Response: {result.get('ai_response', 'No response')[:60]}...")
            else:
                print(f"❌ Failed: {message} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing message '{message}': {str(e)}")
    
    print()

def test_sms_functionality():
    """Test SMS sending functionality"""
    print("📱 Testing SMS Functionality...")
    
    try:
        payload = {
            "phone_number": TEST_PHONE,
            "message": "🤱 Test message from MAMA-AI! This is a system test."
        }
        
        response = requests.post(
            f"{FLASK_APP_URL}/test-sms",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ SMS sending functionality works")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ SMS test failed - Status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing SMS: {str(e)}")
    
    print()

def test_ussd_simulation():
    """Simulate USSD interactions"""
    print("📞 Testing USSD Simulation...")
    
    ussd_flows = [
        {
            "name": "Main Menu",
            "data": {
                "sessionId": "test_session_1",
                "serviceCode": "*123#",
                "phoneNumber": TEST_PHONE,
                "text": ""
            }
        },
        {
            "name": "Check Symptoms",
            "data": {
                "sessionId": "test_session_2", 
                "serviceCode": "*123#",
                "phoneNumber": TEST_PHONE,
                "text": "2*Nina maumivu ya kichwa"
            }
        },
        {
            "name": "Language Selection",
            "data": {
                "sessionId": "test_session_3",
                "serviceCode": "*123#", 
                "phoneNumber": TEST_PHONE,
                "text": "5*2"  # Select Swahili
            }
        }
    ]
    
    for flow in ussd_flows:
        try:
            response = requests.post(
                f"{FLASK_APP_URL}/ussd",
                data=flow["data"],
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                print(f"✅ {flow['name']}: Working")
                print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ {flow['name']}: Failed - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {flow['name']}: {str(e)}")
    
    print()

def test_database_connection():
    """Test database connection and basic operations"""
    print("🗄️ Testing Database Connection...")
    
    try:
        # Import after setting up path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app import app, db
        from src.models import User, Conversation
        
        with app.app_context():
            # Test database connection
            user_count = User.query.count()
            conversation_count = Conversation.query.count()
            
            print(f"✅ Database connected successfully")
            print(f"   Users: {user_count}")
            print(f"   Conversations: {conversation_count}")
            
            # Test creating a user
            test_user = User.query.filter_by(phone_number=TEST_PHONE).first()
            if not test_user:
                test_user = User(
                    phone_number=TEST_PHONE,
                    name="Test User",
                    preferred_language="en",
                    is_active=True
                )
                db.session.add(test_user)
                db.session.commit()
                print("✅ Test user created")
            else:
                print("✅ Test user already exists")
                
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
    
    print()

def test_ai_service_directly():
    """Test AI service directly"""
    print("🧠 Testing AI Service Directly...")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from src.services.ai_service import AIService
        from src.models import User
        from app import app
        
        with app.app_context():
            ai_service = AIService()
            
            # Create test user
            test_user = User(
                id=999,
                phone_number=TEST_PHONE,
                name="Test User",
                preferred_language="en"
            )
            
            # Test AI chat
            response = ai_service.chat_with_ai(
                "I have a headache and feel tired",
                test_user,
                "test_session",
                "SMS"
            )
            
            if response:
                print("✅ AI service working")
                print(f"   Response: {response[:100]}...")
            else:
                print("❌ AI service returned no response")
                
    except Exception as e:
        print(f"❌ AI service test failed: {str(e)}")
    
    print()

def check_environment():
    """Check environment configuration"""
    print("🔧 Checking Environment Configuration...")
    
    required_vars = [
        "GITHUB_TOKEN",
        "MYSQL_HOST", 
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DATABASE",
        "AFRICASTALKING_API_KEY",
        "AFRICASTALKING_SHORTCODE"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "TOKEN" in var or "PASSWORD" in var or "KEY" in var:
                masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
    else:
        print("\n✅ All required environment variables are set")
    
    print()

def main():
    """Run all tests"""
    print("🚀 MAMA-AI Integration Test Suite")
    print("=" * 50)
    print(f"Testing against: {FLASK_APP_URL}")
    print(f"Test phone: {TEST_PHONE}")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    check_environment()
    test_database_connection()
    test_ai_service_directly()
    test_ai_chat()
    test_sms_functionality()
    test_ussd_simulation()
    
    print("🎉 Test suite completed!")
    print("\nIf all tests passed, your MAMA-AI system is ready!")
    print("\nTo test with real devices:")
    print("1. Send SMS to your shortcode (15629)")
    print("2. Dial *123# on a mobile phone")
    print("3. Check the conversation logs in the database")

if __name__ == "__main__":
    main()
