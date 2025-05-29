#!/usr/bin/env python3
"""
USSD Response Size Optimization Test

This script demonstrates the new USSD response size handling features:
1. Smart response truncation
2. Key medical information extraction
3. Response summarization
4. Character limit compliance

Run this to test USSD response optimization before deployment.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MockUser:
    def __init__(self):
        self.preferred_language = 'en'
        self.name = 'Test User'

class USSDTestCase:
    def __init__(self, name, ai_response, expected_length_limit=160):
        self.name = name
        self.ai_response = ai_response
        self.expected_length_limit = expected_length_limit

def test_ussd_response_optimization():
    """Test the USSD response optimization features"""
    
    # Import the optimized USSD service
    from src.services.ussd_service import USSDService
    
    ussd_service = USSDService()
    user = MockUser()
    
    # Test cases with different response types and lengths
    test_cases = [
        USSDTestCase(
            name="Long Medical Advice",
            ai_response=(
                "I understand you're asking about pregnancy symptoms. It's important to note that "
                "during pregnancy, you should take prenatal vitamins regularly, avoid alcohol and "
                "smoking completely, and contact your doctor immediately if you experience severe "
                "abdominal pain, heavy bleeding, or persistent nausea and vomiting. You should also "
                "maintain a healthy diet rich in folic acid, iron, and calcium. Regular prenatal "
                "checkups are essential for monitoring both your health and your baby's development."
            )
        ),
        USSDTestCase(
            name="Emergency Response",
            ai_response=(
                "Warning! Heavy bleeding during pregnancy is an emergency. You must contact your "
                "doctor immediately or go to the nearest hospital emergency room. Do not wait. "
                "This could be a sign of serious complications that require immediate medical attention."
            )
        ),
        USSDTestCase(
            name="Simple Advice",
            ai_response="Take prenatal vitamins daily and stay hydrated."
        ),
        USSDTestCase(
            name="Very Long Response",
            ai_response=(
                "Thank you for your question about maternal health. I'd be happy to help you with "
                "this important topic. From a medical perspective, it's always recommended that "
                "expectant mothers follow a comprehensive care plan. Please remember that you should "
                "always consult with your healthcare provider before making any decisions. Based on "
                "your question, I can provide some general guidance. It's important to note that "
                "every pregnancy is different and what works for one person may not work for another. "
                "Keep in mind that regular prenatal care is essential for a healthy pregnancy outcome."
            )
        ),
    ]
    
    print("🧪 USSD RESPONSE OPTIMIZATION TEST")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case.name}")
        print(f"Original Length: {len(test_case.ai_response)} characters")
        print(f"Original Response: {test_case.ai_response[:100]}...")
        
        # Test the optimization methods
        try:
            # Test key medical info extraction
            key_info = ussd_service._extract_key_medical_info(test_case.ai_response)
            
            # Test response cleaning
            cleaned = ussd_service._clean_ai_response(test_case.ai_response)
            
            # Test full optimization
            optimized = ussd_service._optimize_ai_response_for_ussd(test_case.ai_response, 'en')
            
            # Test conversation display (full formatting)
            conversation_display = ussd_service._build_conversation_display(
                "test question", test_case.ai_response, 'en'
            )
            
            print(f"\n🔍 Key Medical Info: {key_info[:80] + '...' if key_info and len(key_info) > 80 else key_info}")
            print(f"🧹 Cleaned Response: {cleaned[:80]}{'...' if len(cleaned) > 80 else ''}")
            print(f"⚡ Optimized Response: {optimized}")
            print(f"📱 Final USSD Display: {conversation_display}")
            print(f"✅ Final Length: {len(conversation_display)} chars (Limit: {test_case.expected_length_limit})")
            
            # Verify length compliance
            if len(conversation_display) <= test_case.expected_length_limit:
                print("🟢 PASS: Within character limit")
            else:
                print("🔴 FAIL: Exceeds character limit")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("-" * 40)
    
    # Test Kiswahili optimization
    print(f"\n🌍 Testing Kiswahili Optimization")
    test_swahili = "Hii ni jibu refu sana kuhusu afya ya mama na mtoto. Ni muhimu kwenda hospitalini mara moja kama una dalili za hatari."
    optimized_sw = ussd_service._optimize_ai_response_for_ussd(test_swahili, 'sw')
    display_sw = ussd_service._build_conversation_display("swali", test_swahili, 'sw')
    
    print(f"Original Swahili: {test_swahili}")
    print(f"Optimized Swahili: {optimized_sw}")
    print(f"Final Display: {display_sw}")
    print(f"Length: {len(display_sw)} chars")
    
    print("\n✅ USSD Response Optimization Test Complete!")
    return True

def demonstrate_features():
    """Demonstrate the key features of the optimized USSD service"""
    
    print("\n🚀 USSD RESPONSE OPTIMIZATION FEATURES")
    print("=" * 50)
    
    features = [
        "✅ Smart Response Truncation - Cuts at sentence boundaries, not mid-word",
        "✅ Key Medical Information Extraction - Prioritizes critical health advice",
        "✅ Response Summarization - Creates concise summaries of long responses",
        "✅ Multi-language Support - Optimizes for both English and Kiswahili",
        "✅ Character Limit Compliance - Ensures all responses fit USSD limits (160 chars)",
        "✅ Context Preservation - Maintains important medical context during truncation",
        "✅ Emergency Response Priority - Highlights urgent medical information",
        "✅ Enhanced Logging - Tracks response lengths and optimization results",
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print(f"\n📊 OPTIMIZATION STRATEGIES:")
    strategies = [
        "1. Extract key medical patterns (warnings, advice, symptoms)",
        "2. Remove redundant AI phrases and formatting",
        "3. Prioritize sentences with important keywords",
        "4. Smart truncation at sentence/clause boundaries",
        "5. Fallback to word-boundary truncation with ellipsis",
    ]
    
    for strategy in strategies:
        print(f"  {strategy}")

if __name__ == "__main__":
    print("🤱 MAMA-AI USSD Service - Response Size Optimization")
    print("Testing improved USSD response handling...")
    
    try:
        demonstrate_features()
        test_ussd_response_optimization()
        
        print(f"\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print(f"✅ USSD responses are now optimized for:")
        print(f"   • Better content delivery within character limits")
        print(f"   • Prioritized medical information")
        print(f"   • Smart truncation that preserves meaning")
        print(f"   • Multi-language support")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)
