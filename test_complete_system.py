#!/usr/bin/env python3
"""
MAMA-AI Complete System Test Suite
Tests all functionality including SMS, USSD, AI responses, and database operations.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://qtcfcmnf-5000.euw.devtunnels.ms"
TEST_PHONE = "+254700000001"

class MamaAITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   {details}")
    
    def test_health_endpoint(self):
        """Test system health and status"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "healthy":
                    self.log_test("Health Check", "PASS", f"Database: {data['services']['database']['status']}")
                    return True
                else:
                    self.log_test("Health Check", "FAIL", f"Status: {data.get('status', 'unknown')}")
            else:
                self.log_test("Health Check", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", "FAIL", str(e))
        return False
    
    def test_sms_webhook(self):
        """Test SMS webhook processing"""
        try:
            test_data = {
                "from": TEST_PHONE,
                "to": "985",
                "text": "Test SMS from automated test",
                "date": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/sms",
                data=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    self.log_test("SMS Webhook", "PASS", "SMS processed successfully")
                    return True
                else:
                    self.log_test("SMS Webhook", "FAIL", f"Status: {data.get('status', 'unknown')}")
            else:
                self.log_test("SMS Webhook", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("SMS Webhook", "FAIL", str(e))
        return False
    
    def test_ai_responses(self):
        """Test AI response generation for various scenarios"""
        test_cases = [
            ("hi", "greeting"),
            ("help", "help command"),
            ("I have back pain", "symptom report"),
            ("emergency", "emergency scenario"),
            ("when is my baby due", "pregnancy question"),
            ("appointment", "appointment query"),
            ("stop", "unsubscribe request")
        ]
        
        passed = 0
        for message, scenario in test_cases:
            try:
                response = requests.get(
                    f"{self.base_url}/test-sms-response",
                    params={"text": message, "from": TEST_PHONE},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success" and data["ai_response"]:
                        self.log_test(f"AI Response ({scenario})", "PASS", 
                                    f"Response: {data['ai_response'][:50]}...")
                        passed += 1
                    else:
                        self.log_test(f"AI Response ({scenario})", "FAIL", 
                                    f"No response generated")
                else:
                    self.log_test(f"AI Response ({scenario})", "FAIL", 
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"AI Response ({scenario})", "FAIL", str(e))
        
        return passed == len(test_cases)
    
    def test_ussd_webhook(self):
        """Test USSD webhook processing"""
        try:
            test_data = {
                "sessionId": "test_session_123",
                "serviceCode": "*985#",
                "phoneNumber": TEST_PHONE,
                "text": ""
            }
            
            response = requests.post(
                f"{self.base_url}/ussd",
                data=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                response_text = response.text
                if "CON" in response_text or "END" in response_text:
                    self.log_test("USSD Webhook", "PASS", f"USSD response: {response_text[:50]}...")
                    return True
                else:
                    self.log_test("USSD Webhook", "FAIL", "Invalid USSD response format")
            else:
                self.log_test("USSD Webhook", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("USSD Webhook", "FAIL", str(e))
        return False
    
    def test_dashboard_access(self):
        """Test testing dashboard accessibility"""
        try:
            response = requests.get(f"{self.base_url}/test-dashboard", timeout=10)
            if response.status_code == 200 and "MAMA-AI Testing Dashboard" in response.text:
                self.log_test("Testing Dashboard", "PASS", "Dashboard accessible")
                return True
            else:
                self.log_test("Testing Dashboard", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Testing Dashboard", "FAIL", str(e))
        return False
    
    def test_stats_endpoint(self):
        """Test system statistics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    stats = data["statistics"]
                    self.log_test("Statistics Endpoint", "PASS", 
                                f"Users: {stats['users']['total']}, "
                                f"Messages: {stats['messages']['total']}")
                    return True
                else:
                    self.log_test("Statistics Endpoint", "FAIL", f"Status: {data.get('status')}")
            else:
                self.log_test("Statistics Endpoint", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Statistics Endpoint", "FAIL", str(e))
        return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting MAMA-AI Complete System Test Suite")
        print("=" * 60)
        
        tests = [
            self.test_health_endpoint,
            self.test_sms_webhook,
            self.test_ai_responses,
            self.test_ussd_webhook,
            self.test_dashboard_access,
            self.test_stats_endpoint
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! MAMA-AI system is fully operational.")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the details above.")
        
        return passed == total
    
    def generate_report(self):
        """Generate detailed test report"""
        report = {
            "test_suite": "MAMA-AI Complete System Test",
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_tests": len(self.test_results),
            "passed": len([r for r in self.test_results if r["status"] == "PASS"]),
            "failed": len([r for r in self.test_results if r["status"] == "FAIL"]),
            "results": self.test_results
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed test report saved to: test_report.json")
        return report

def main():
    """Main test execution"""
    print("🤱 MAMA-AI System Testing Suite")
    print(f"🌐 Testing URL: {BASE_URL}")
    print(f"📱 Test Phone: {TEST_PHONE}")
    print()
    
    tester = MamaAITester()
    success = tester.run_all_tests()
    tester.generate_report()
    
    if success:
        print("\n✨ MAMA-AI is perfect and ready for production! ✨")
    else:
        print("\n🔧 Some issues detected. Please check the logs above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
