#!/usr/bin/env python3
"""
Test script for Africa's Talking Voice API integration
This script helps you test voice functionality locally
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_voice_callback():
    """Test the voice callback endpoint"""
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Test data that simulates Africa's Talking voice callback
    test_data = {
        'sessionId': 'test_session_123',
        'phoneNumber': '+254700000000',
        'isActive': '1',
        'dtmfDigits': '',  # Empty for initial call
        'recordingUrl': '',
        'durationInSeconds': '0',
        'direction': 'Inbound',
        'amount': '0',
        'currencyCode': 'KES'
    }
    
    try:
        response = requests.post(f'{base_url}/voice', data=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Voice callback test successful!")
        else:
            print("❌ Voice callback test failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the application.")
        print("Make sure your Flask app is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_dtmf_input():
    """Test DTMF input handling"""
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Test data simulating user pressing '1' for symptoms
    test_data = {
        'sessionId': 'test_session_123',
        'phoneNumber': '+254700000000',
        'isActive': '1',
        'dtmfDigits': '1',  # User pressed 1
        'recordingUrl': '',
        'durationInSeconds': '5',
        'direction': 'Inbound',
        'amount': '0',
        'currencyCode': 'KES'
    }
    
    try:
        response = requests.post(f'{base_url}/voice', data=test_data)
        print(f"\nDTMF Input Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ DTMF input test successful!")
        else:
            print("❌ DTMF input test failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_voice_recording():
    """Test voice recording callback"""
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Test data simulating voice recording
    test_data = {
        'sessionId': 'test_session_123',
        'phoneNumber': '+254700000000',
        'isActive': '1',
        'dtmfDigits': '',
        'recordingUrl': 'https://test-recording-url.com/recording.wav',
        'durationInSeconds': '15',
        'direction': 'Inbound',
        'amount': '0',
        'currencyCode': 'KES'
    }
    
    try:
        response = requests.post(f'{base_url}/voice', data=test_data)
        print(f"\nVoice Recording Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Voice recording test successful!")
        else:
            print("❌ Voice recording test failed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🎙️ Testing MAMA-AI Voice Integration")
    print("="*50)
    
    # Check if app is running
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    try:
        health_response = requests.get(f'{base_url}/health')
        if health_response.status_code == 200:
            print("✅ Application is running!")
        else:
            print("❌ Application health check failed!")
            sys.exit(1)
    except:
        print("❌ Application is not running. Please start it first with: python app.py")
        sys.exit(1)
    
    # Run tests
    test_voice_callback()
    test_dtmf_input()
    test_voice_recording()
    
    print("\n" + "="*50)
    print("🎉 Voice testing complete!")
    print("\nNext steps:")
    print("1. Configure your Africa's Talking voice number")
    print("2. Set the callback URL to: https://yourdomain.com/voice")
    print("3. Test with real phone calls")
