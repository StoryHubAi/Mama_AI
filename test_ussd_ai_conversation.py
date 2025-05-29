#!/usr/bin/env python3
"""
Test script to verify USSD AI conversation flow
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_ussd_ai_conversation():
    """Test the USSD AI conversation flow"""
    
    print("🧪 Testing USSD AI Conversation Flow")
    print("=" * 50)
    
    try:
        from src.services.ussd_service import USSDService
        
        # Create USSD service instance
        ussd_service = USSDService()
        
        print("✅ USSD Service initialized successfully")
        
        # Test conversation flow
        print("\n📱 Simulating USSD conversation...")
        
        # Simulate user with existing registration
        class MockUser:
            def __init__(self):
                self.id = 1
                self.name = "Test Mama"
                self.preferred_language = "en"
                self.phone_number = "+254712345678"
        
        class MockPregnancy:
            def __init__(self):
                self.weeks_pregnant = 20
        
        user = MockUser()
        pregnancy = MockPregnancy()
        
        # Mock the _get_active_pregnancy method
        def mock_get_active_pregnancy(user):
            return pregnancy
        
        ussd_service._get_active_pregnancy = mock_get_active_pregnancy
        
        # Test main menu selection for chat
        session_id = "test_session_123"
        
        print("\n1️⃣ Testing main menu selection for 'Chat with MAMA-AI'...")
        response = ussd_service._handle_main_menu_selection('1', user, session_id)
        print(f"Response: {response}")
        
        if "Chat with MAMA-AI" in response and "Enter your health question:" in response:
            print("✅ Chat prompt displays correctly")
        else:
            print("❌ Chat prompt not displaying correctly")
            return False
        
        # Test multi-step interaction simulation
        print("\n2️⃣ Testing AI conversation flow...")
        
        # Simulate user typing a health question
        inputs = ['1', 'I have morning sickness']  # Option 1 (chat) + user message
        
        # Check if AI service is available
        if ussd_service.ai_service.client:
            print("✅ AI service is available")
            
            try:
                response = ussd_service._handle_multi_step_interaction(inputs, user, session_id)
                print(f"AI Response: {response}")
                
                # Check if response contains conversation elements
                if "CON" in response and ("You:" in response or "AI:" in response):
                    print("✅ Conversation display working correctly")
                elif "END" in response and "AI" in response:
                    print("⚠️ AI responded but ended session (possibly due to AI unavailability)")
                else:
                    print("❌ Conversation display not working correctly")
                    return False
                    
            except Exception as e:
                print(f"❌ Error in conversation flow: {str(e)}")
                return False
        else:
            print("⚠️ AI service not available - testing fallback...")
            response = ussd_service._handle_multi_step_interaction(inputs, user, session_id)
            if "AI not available" in response or "AI haipo" in response:
                print("✅ AI unavailability handled correctly")
            else:
                print("❌ AI unavailability not handled correctly")
                return False
        
        print("\n3️⃣ Testing conversation display formatting...")
        
        # Test the conversation display function
        test_user_msg = "I have headaches"
        test_ai_response = "Headaches during pregnancy can be common. Stay hydrated and rest. If severe or persistent, consult your doctor."
        
        display = ussd_service._build_conversation_display(test_user_msg, test_ai_response, "en")
        print(f"Display format: {display}")
        
        if "You:" in display and "AI:" in display:
            print("✅ Conversation display format correct")
        else:
            print("❌ Conversation display format incorrect")
            return False
        
        print("\n🎉 All USSD AI conversation tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ussd_ai_conversation()
    sys.exit(0 if success else 1)
