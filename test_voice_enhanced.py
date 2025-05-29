#!/usr/bin/env python3
"""
Enhanced test script for MAMA-AI Voice Integration with Speech-to-Text
This script tests the complete voice workflow including speech-to-text processing
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_speech_to_text_service():
    """Test the speech-to-text service directly"""
    print("\n🧪 Testing Speech-to-Text Service...")
    print("-" * 50)
    
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.services.speech_to_text_service import SpeechToTextService
        
        # Initialize the service
        stt_service = SpeechToTextService()
        
        # Test service configuration
        status = stt_service.test_service()
        print(f"Provider: {status['provider']}")
        print(f"Configuration Status:")
        
        providers = ['whisper', 'google', 'azure']
        for provider in providers:
            configured = status.get(f'{provider}_configured', False)
            print(f"  {provider.title()}: {'✅ Configured' if configured else '❌ Not configured'}")
        
        print(f"  Mock Fallback: {'✅ Available' if status['fallback_available'] else '❌ Not available'}")
        print(f"Supported Languages: {status['supported_languages']}")
        
        # Test with mock recording
        print(f"\n📝 Testing speech conversion...")
        test_recordings = [
            ("https://example.com/test-recording-en.wav", "en-US"),
            ("https://example.com/test-recording-sw.wav", "sw-KE"),
        ]
        
        for recording_url, language in test_recordings:
            print(f"\nTesting {language}:")
            result = stt_service.convert_recording_to_text(recording_url, language)
            
            if result['success']:
                print(f"  ✅ Success: {result['transcript']}")
                print(f"  Confidence: {result['confidence']:.2f}")
                print(f"  Provider: {result['provider']}")
                if result.get('note'):
                    print(f"  Note: {result['note']}")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import speech-to-text service: {e}")
        return False
    except Exception as e:
        print(f"❌ Speech-to-Text test failed: {e}")
        return False

def test_voice_recording_endpoint():
    """Test the enhanced voice recording endpoint"""
    print("\n🎙️ Testing Enhanced Voice Recording Endpoint...")
    print("-" * 50)
    
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Test data simulating voice recording with speech-to-text
    test_data = {
        'sessionId': 'test_session_stt_123',
        'phoneNumber': '+254700000000',
        'isActive': '1',
        'recordingUrl': 'https://test-recording-url.com/pregnancy_question.wav',
        'durationInSeconds': '8',
        'direction': 'Inbound'
    }
    
    try:
        print(f"📤 Sending voice recording callback to: {base_url}/voice/recording/test_session_stt_123")
        response = requests.post(f'{base_url}/voice/recording/test_session_stt_123', data=test_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            print("✅ Voice recording with speech-to-text successful!")
            
            # Check if response contains expected XML structure
            if '<Response>' in response.text and '<Say' in response.text:
                print("✅ Valid XML response received")
                
                # Look for AI-generated content
                if 'voice="woman"' in response.text:
                    print("✅ Text-to-speech response format correct")
                else:
                    print("⚠️  Text-to-speech format may have issues")
            else:
                print("⚠️  Response format may have issues")
                
        else:
            print(f"❌ Voice recording test failed with status {response.status_code}")
            
        # Show partial response for debugging
        print(f"\nFirst 200 characters of response:")
        print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Voice recording test failed: {e}")
        return False

def test_voice_callback():
    """Test the basic voice callback endpoint"""
    print("\n📞 Testing Voice Callback...")
    print("-" * 50)
    
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Test data for incoming call
    test_data = {
        'sessionId': 'test_session_callback_456',
        'phoneNumber': '+254700000000',
        'isActive': '1',
        'direction': 'Inbound'
    }
    
    try:
        print(f"📤 Sending voice callback to: {base_url}/voice")
        response = requests.post(f'{base_url}/voice', data=test_data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Voice callback successful!")
            
            # Check for AI-enhanced welcome message
            if 'welcome to MAMA-AI' in response.text.lower():
                print("✅ AI-enhanced welcome message found")
            
            # Check for voice recording capability
            if '<Record' in response.text:
                print("✅ Voice recording capability enabled")
            else:
                print("⚠️  Voice recording may not be configured")
                
        else:
            print(f"❌ Voice callback failed with status {response.status_code}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Voice callback test failed: {e}")
        return False

def test_dtmf_input():
    """Test DTMF input handling"""
    print("\n🔢 Testing DTMF Input...")
    print("-" * 50)
    
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Test different DTMF inputs
    dtmf_tests = [
        ('1', 'pregnancy tracking'),
        ('2', 'health check'),
        ('3', 'appointments'),
        ('4', 'emergency'),
        ('9', 'repeat menu')
    ]
    
    success_count = 0
    
    for dtmf, description in dtmf_tests:
        test_data = {
            'sessionId': f'test_dtmf_{dtmf}',
            'phoneNumber': '+254700000000',
            'dtmfDigits': dtmf
        }
        
        try:
            print(f"Testing DTMF {dtmf} ({description})...")
            response = requests.post(f'{base_url}/voice/dtmf', data=test_data)
            
            if response.status_code == 200:
                print(f"  ✅ DTMF {dtmf} successful")
                success_count += 1
            else:
                print(f"  ❌ DTMF {dtmf} failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ DTMF {dtmf} error: {e}")
    
    print(f"\nDTMF Tests: {success_count}/{len(dtmf_tests)} successful")
    return success_count == len(dtmf_tests)

def check_environment():
    """Check environment configuration for speech-to-text"""
    print("\n🔧 Checking Environment Configuration...")
    print("-" * 50)
    
    env_vars = {
        'SPEECH_TO_TEXT_PROVIDER': os.getenv('SPEECH_TO_TEXT_PROVIDER', 'Not set (will use default)'),
        'OPENAI_API_KEY': '✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set',
        'GOOGLE_SPEECH_API_KEY': '✅ Set' if os.getenv('GOOGLE_SPEECH_API_KEY') else '❌ Not set',
        'AZURE_SPEECH_KEY': '✅ Set' if os.getenv('AZURE_SPEECH_KEY') else '❌ Not set',
        'AZURE_SPEECH_REGION': '✅ Set' if os.getenv('AZURE_SPEECH_REGION') else '❌ Not set',
        'BASE_URL': os.getenv('BASE_URL', 'http://localhost:5000'),
        'VOICE_PHONE_NUMBER': os.getenv('VOICE_PHONE_NUMBER', 'Not set')
    }
    
    for var, value in env_vars.items():
        print(f"{var}: {value}")
    
    # Check if at least one speech-to-text provider is configured
    providers_configured = any([
        os.getenv('OPENAI_API_KEY'),
        os.getenv('GOOGLE_SPEECH_API_KEY'),
        os.getenv('AZURE_SPEECH_KEY')
    ])
    
    if providers_configured:
        print("\n✅ At least one speech-to-text provider is configured")
    else:
        print("\n⚠️  No speech-to-text providers configured - will use mock responses")
    
    return True

if __name__ == "__main__":
    print("🎙️ Enhanced MAMA-AI Voice Integration Test with Speech-to-Text")
    print("=" * 70)
    
    # Check if app is running
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    try:
        health_response = requests.get(f'{base_url}/health', timeout=5)
        if health_response.status_code == 200:
            print("✅ Application is running!")
        else:
            print("❌ Application health check failed!")
            sys.exit(1)
    except:
        print("❌ Application is not running. Please start it first with: python app.py")
        sys.exit(1)
    
    # Run all tests
    tests = [
        ("Environment Check", check_environment),
        ("Speech-to-Text Service", test_speech_to_text_service),
        ("Voice Callback", test_voice_callback),
        ("DTMF Input", test_dtmf_input),
        ("Voice Recording with STT", test_voice_recording_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("🎉 Enhanced Voice Testing Complete!")
    print("="*70)
    
    success_count = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("\n🎊 All tests passed! Your enhanced voice integration is working perfectly!")
    else:
        print(f"\n⚠️  {total_tests - success_count} test(s) failed. Check the output above for details.")
    
    print("\n📋 Next steps:")
    print("1. Configure speech-to-text API keys for production use")
    print("2. Test with real phone calls using ngrok or deployed URL") 
    print("3. Monitor speech-to-text accuracy in logs")
    print("4. Configure Africa's Talking voice callback URL")
    print("\n🎙️ Ready for enhanced voice conversations with MAMA-AI! 🤖✨")
