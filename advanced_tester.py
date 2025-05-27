#!/usr/bin/env python3
"""
MAMA-AI Advanced Testing Suite
Comprehensive testing tool for Africa's Talking integration
"""

import requests
import json
import time
import random
from datetime import datetime
from urllib.parse import urlencode

class MamaAITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_numbers = [
            "+254700000001", "+254700000002", "+254700000003",
            "+254700000004", "+254700000005", "+254700000006"
        ]
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def send_sms(self, phone_number, message):
        """Send SMS via test endpoint"""
        try:
            response = self.session.post(
                f"{self.base_url}/test-sms",
                json={"phone_number": phone_number, "message": message}
            )
            result = response.json()
            self.log(f"📤 SMS sent to {phone_number}: {result.get('message', 'Failed')}")
            return response.status_code == 200
        except Exception as e:
            self.log(f"❌ SMS send error: {e}", "ERROR")
            return False
            
    def simulate_incoming_sms(self, from_number, message, to_shortcode="985"):
        """Simulate incoming SMS"""
        try:
            data = {
                "from": from_number,
                "to": to_shortcode,
                "text": message,
                "date": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/sms",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            result = response.json()
            self.log(f"📩 Incoming SMS from {from_number}: {result.get('status', 'Failed')}")
            return response.status_code == 200
        except Exception as e:
            self.log(f"❌ Incoming SMS error: {e}", "ERROR")
            return False
            
    def simulate_ussd_session(self, phone_number, inputs):
        """Simulate complete USSD session"""
        session_id = f"session_{int(time.time())}"
        text = ""
        
        self.log(f"📞 Starting USSD session {session_id} for {phone_number}")
        
        for i, input_val in enumerate(inputs):
            if i > 0:
                text += "*" + str(input_val)
            else:
                text = str(input_val)
                
            try:
                data = {
                    "sessionId": session_id,
                    "serviceCode": "*123#",
                    "phoneNumber": phone_number,
                    "text": text
                }
                
                response = self.session.post(
                    f"{self.base_url}/ussd",
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                result = response.text
                self.log(f"📞 USSD Step {i+1}: Input '{input_val}' -> Response: {result[:100]}...")
                
                if result.startswith("END"):
                    self.log("📞 USSD session ended")
                    break
                    
                time.sleep(1)  # Simulate user thinking time
                
            except Exception as e:
                self.log(f"❌ USSD error: {e}", "ERROR")
                break
                
    def test_emergency_scenarios(self):
        """Test various emergency scenarios"""
        self.log("🚨 Testing Emergency Scenarios")
        
        emergencies = [
            "EMERGENCY: I have severe bleeding and cramping. Please help!",
            "I can't feel my baby moving for 6 hours. Should I be worried?",
            "I have terrible headache and blurred vision. Is this normal?",
            "I'm having contractions every 3 minutes at 35 weeks",
            "I fell down stairs and hit my belly hard. What should I do?",
            "I'm experiencing severe pain in my abdomen and back",
            "My water broke but I'm only 32 weeks pregnant!"
        ]
        
        for i, emergency in enumerate(emergencies):
            phone = self.test_numbers[i % len(self.test_numbers)]
            self.simulate_incoming_sms(phone, emergency)
            time.sleep(2)
            
    def test_regular_queries(self):
        """Test regular health queries"""
        self.log("💊 Testing Regular Health Queries")
        
        queries = [
            "What foods should I avoid during pregnancy?",
            "How often should I feel baby movements?",
            "I'm experiencing morning sickness. What can I do?",
            "When should I schedule my next appointment?",
            "Is it safe to exercise during pregnancy?",
            "What vitamins should I take?",
            "I have back pain. Is this normal?",
            "How much weight should I gain?",
            "What are the signs of labor?",
            "Can I travel during pregnancy?"
        ]
        
        for i, query in enumerate(queries):
            phone = self.test_numbers[i % len(self.test_numbers)]
            self.simulate_incoming_sms(phone, query)
            time.sleep(1.5)
            
    def test_multilingual(self):
        """Test Kiswahili support"""
        self.log("🗣️ Testing Multilingual Support")
        
        kiswahili_messages = [
            "Habari, nina mimba ya miezi mitatu. Ninahisi kichefuchefu asubuhi.",
            "Je, ni vyakula gani nisivyokula wakati wa ujauzito?",
            "Nina maumivu ya mgongo. Je, hii ni kawaida?",
            "Mfumo wa chakula gani ni bora wakati wa ujauzito?",
            "Je, nina haja ya kuonana na daktari mara ngapi?",
            "Ninahisi kuchoka sana. Je, hii ni kawaida?"
        ]
        
        for i, message in enumerate(kiswahili_messages):
            phone = self.test_numbers[i % len(self.test_numbers)]
            self.simulate_incoming_sms(phone, message)
            time.sleep(2)
            
    def test_ussd_flows(self):
        """Test different USSD navigation flows"""
        self.log("📞 Testing USSD Flows")
        
        # Test main menu navigation
        flows = [
            ["1"],  # Chat with AI
            ["2"],  # Schedule appointment
            ["3"],  # Health tips
            ["4"],  # Emergency help
            ["5"],  # Language settings
            ["1", "1"],  # Chat -> Emergency
            ["2", "1"],  # Appointment -> Schedule new
            ["3", "1"],  # Tips -> Nutrition
            ["5", "2"]   # Language -> Kiswahili
        ]
        
        for i, flow in enumerate(flows):
            phone = self.test_numbers[i % len(self.test_numbers)]
            self.simulate_ussd_session(phone, flow)
            time.sleep(3)
            
    def test_load_simulation(self, num_users=20, duration=60):
        """Simulate load with multiple concurrent users"""
        self.log(f"⚡ Load Testing: {num_users} users for {duration}s")
        
        messages = [
            "Hello, I need help with pregnancy advice",
            "I'm feeling nauseous, what should I do?",
            "When is my next appointment?",
            "I have questions about nutrition",
            "Is exercise safe during pregnancy?",
            "What are warning signs I should watch for?"
        ]
        
        start_time = time.time()
        requests_sent = 0
        
        while time.time() - start_time < duration:
            for i in range(min(5, num_users)):  # Send 5 at a time
                phone = f"+254700{random.randint(100000, 999999)}"
                message = random.choice(messages)
                
                if self.simulate_incoming_sms(phone, message):
                    requests_sent += 1
                    
            time.sleep(1)
            
        self.log(f"⚡ Load test completed: {requests_sent} requests in {duration}s")
        
    def test_edge_cases(self):
        """Test edge cases and error scenarios"""
        self.log("🔧 Testing Edge Cases")
        
        # Empty messages
        self.simulate_incoming_sms("+254700000001", "")
        
        # Very long messages
        long_message = "A" * 1000
        self.simulate_incoming_sms("+254700000002", long_message)
        
        # Special characters
        self.simulate_incoming_sms("+254700000003", "Hello! @#$%^&*()_+{}[]|\\:;\"'<>?,./")
        
        # Invalid phone numbers
        self.simulate_incoming_sms("invalid", "Test message")
        
        # Different encoding
        self.simulate_incoming_sms("+254700000004", "🤰👶🍼💊🏥")
        
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        self.log("🚀 Starting Comprehensive Test Suite")
        
        tests = [
            ("Emergency Scenarios", self.test_emergency_scenarios),
            ("Regular Queries", self.test_regular_queries),
            ("Multilingual Support", self.test_multilingual),
            ("USSD Flows", self.test_ussd_flows),
            ("Edge Cases", self.test_edge_cases)
        ]
        
        for test_name, test_func in tests:
            self.log(f"▶️ Running {test_name}")
            try:
                test_func()
                self.log(f"✅ {test_name} completed")
            except Exception as e:
                self.log(f"❌ {test_name} failed: {e}", "ERROR")
            
            time.sleep(5)  # Pause between test suites
            
        self.log("🎉 Comprehensive test suite completed!")
        
    def interactive_menu(self):
        """Interactive testing menu"""
        while True:
            print("\n" + "="*50)
            print("🤱 MAMA-AI Testing Suite")
            print("="*50)
            print("1. Test Emergency Scenarios")
            print("2. Test Regular Health Queries")
            print("3. Test Multilingual Support")
            print("4. Test USSD Flows")
            print("5. Test Edge Cases")
            print("6. Load Testing")
            print("7. Run Comprehensive Test")
            print("8. Custom SMS Test")
            print("9. Custom USSD Test")
            print("0. Exit")
            
            choice = input("\nSelect option (0-9): ").strip()
            
            if choice == "0":
                self.log("👋 Goodbye!")
                break
            elif choice == "1":
                self.test_emergency_scenarios()
            elif choice == "2":
                self.test_regular_queries()
            elif choice == "3":
                self.test_multilingual()
            elif choice == "4":
                self.test_ussd_flows()
            elif choice == "5":
                self.test_edge_cases()
            elif choice == "6":
                users = int(input("Number of users (default 20): ") or "20")
                duration = int(input("Duration in seconds (default 60): ") or "60")
                self.test_load_simulation(users, duration)
            elif choice == "7":
                self.run_comprehensive_test()
            elif choice == "8":
                phone = input("Phone number (+254700000000): ").strip()
                message = input("Message: ").strip()
                if phone and message:
                    self.simulate_incoming_sms(phone, message)
            elif choice == "9":
                phone = input("Phone number (+254700000000): ").strip()
                inputs_str = input("USSD inputs (comma-separated, e.g., 1,2,3): ").strip()
                if phone and inputs_str:
                    inputs = [x.strip() for x in inputs_str.split(",")]
                    self.simulate_ussd_session(phone, inputs)
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    tester = MamaAITester()
    tester.interactive_menu()

if __name__ == "__main__":
    main()
