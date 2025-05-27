#!/usr/bin/env python3
"""
SMS Testing Script for MAMA-AI
This script allows you to test SMS functionality without the web interface.
"""

import requests
import json
from urllib.parse import quote

# Base URL for your MAMA-AI application
BASE_URL = "http://localhost:5000"

def send_test_sms(phone_number, message):
    """Send a test SMS using the /test-sms endpoint"""
    url = f"{BASE_URL}/test-sms"
    data = {
        "phone_number": phone_number,
        "message": message
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"✅ SMS Sent to {phone_number}")
        print(f"📱 Message: {message}")
        print(f"📊 Result: {result['message']}")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
        return False

def simulate_incoming_sms(from_number, message, to_shortcode="985"):
    """Simulate an incoming SMS to test the AI response"""
    url = f"{BASE_URL}/sms"
    
    # URL encode the message
    encoded_message = quote(message)
    encoded_from = quote(from_number)
    
    data = f"from={encoded_from}&to={to_shortcode}&text={encoded_message}&date=2025-05-27 18:40:00"
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        response = requests.post(url, data=data, headers=headers)
        result = response.json()
        print(f"📩 Incoming SMS from {from_number}")
        print(f"💬 Message: {message}")
        print(f"🤖 AI Response Status: {result['status']}")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ Error processing incoming SMS: {e}")
        return False

def test_emergency_scenarios():
    """Test various emergency scenarios"""
    print("🚨 Testing Emergency Scenarios")
    print("=" * 50)
    
    emergency_messages = [
        "+254700000001|I have severe bleeding and cramping. Please help!",
        "+254700000002|EMERGENCY: I can't feel my baby moving for 6 hours",
        "+254700000003|I have terrible headache and blurred vision",
        "+254700000004|I'm having contractions every 3 minutes at 35 weeks",
        "+254700000005|I fell down stairs and hit my belly hard"
    ]
    
    for msg in emergency_messages:
        phone, text = msg.split("|")
        simulate_incoming_sms(phone, text)

def test_regular_queries():
    """Test regular maternal health queries"""
    print("💊 Testing Regular Health Queries")
    print("=" * 50)
    
    regular_messages = [
        "+254700000006|What foods should I avoid during pregnancy?",
        "+254700000007|Ninahisi kichefuchefu asubuhi. Nifanye nini?",  # Kiswahili
        "+254700000008|How often should I feel baby movements?",
        "+254700000009|When is my next appointment?",
        "+254700000010|I'm experiencing back pain. Is this normal?"
    ]
    
    for msg in regular_messages:
        phone, text = msg.split("|")
        simulate_incoming_sms(phone, text)

def test_sms_sending():
    """Test sending SMS to different numbers"""
    print("📤 Testing SMS Sending")
    print("=" * 50)
    
    test_numbers = [
        "+254700000011",
        "+254700000012", 
        "+254700000013"
    ]
    
    messages = [
        "Hello! Welcome to MAMA-AI. How can I help you today?",
        "Reminder: Your prenatal appointment is tomorrow at 2 PM.",
        "Health Tip: Remember to take your prenatal vitamins daily."
    ]
    
    for i, number in enumerate(test_numbers):
        send_test_sms(number, messages[i])

def main():
    print("🤱 MAMA-AI SMS Testing Suite")
    print("=" * 50)
    
    while True:
        print("\nChoose a test option:")
        print("1. Send test SMS")
        print("2. Simulate incoming SMS")
        print("3. Test emergency scenarios")
        print("4. Test regular health queries")
        print("5. Test SMS sending to multiple numbers")
        print("6. Run all tests")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            phone = input("Enter phone number (+254700000000): ").strip()
            message = input("Enter message: ").strip()
            send_test_sms(phone, message)
        elif choice == "2":
            phone = input("Enter sender phone number (+254700000000): ").strip()
            message = input("Enter message: ").strip()
            simulate_incoming_sms(phone, message)
        elif choice == "3":
            test_emergency_scenarios()
        elif choice == "4":
            test_regular_queries()
        elif choice == "5":
            test_sms_sending()
        elif choice == "6":
            print("🔄 Running all tests...\n")
            test_sms_sending()
            test_regular_queries()
            test_emergency_scenarios()
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
