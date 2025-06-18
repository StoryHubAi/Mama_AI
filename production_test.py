#!/usr/bin/env python3
"""
MAMA-AI Final Production Test Suite
Comprehensive testing before deployment
"""
import requests
import json
import time
import sys
from datetime import datetime

class ProductionTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def log_test(self, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test("Health Check", True, "System healthy")
                    return True
                else:
                    self.log_test("Health Check", False, f"Status: {data.get('status')}")
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
        return False
    
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    stats = data.get('statistics', {})
                    user_count = stats.get('users', {}).get('total', 0)
                    self.log_test("Database Connection", True, f"Connected, {user_count} users")
                    return True
            self.log_test("Database Connection", False, "Stats endpoint failed")
        except Exception as e:
            self.log_test("Database Connection", False, f"Error: {str(e)}")
        return False
    
    def test_sms_simulation(self):
        """Test SMS response simulation"""
        test_messages = [
            "hi",
            "help",
            "I have back pain",
            "emergency bleeding",
            "when is baby due"
        ]
        
        for message in test_messages:
            try:
                payload = {
                    "from": "+254700000001",
                    "text": message
                }
                response = requests.post(
                    f"{self.base_url}/test-sms-response",
                    json=payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success' and data.get('ai_response'):
                        self.log_test(f"SMS Test: '{message}'", True, 
                                    f"Response: {data['ai_response'][:50]}...")
                    else:
                        self.log_test(f"SMS Test: '{message}'", False, "No AI response")
                else:
                    self.log_test(f"SMS Test: '{message}'", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"SMS Test: '{message}'", False, f"Error: {str(e)}")
        
        return True
    
    def test_chat_interface(self):
        """Test chat API endpoint"""
        try:
            payload = {
                "message": "Hello, I'm pregnant and have questions",
                "phone_number": "+254700000001"
            }
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and data.get('response'):
                    self.log_test("Chat Interface", True, 
                                f"Response: {data['response'][:50]}...")
                    return True
            
            self.log_test("Chat Interface", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Chat Interface", False, f"Error: {str(e)}")
        return False
    
    def test_ui_endpoints(self):
        """Test UI endpoints accessibility"""
        ui_endpoints = [
            "/test-dashboard",
            "/chat-interface"
        ]
        
        for endpoint in ui_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200 and len(response.text) > 1000:
                    self.log_test(f"UI Endpoint {endpoint}", True, "Accessible")
                else:
                    self.log_test(f"UI Endpoint {endpoint}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"UI Endpoint {endpoint}", False, f"Error: {str(e)}")
    
    def test_webhook_endpoints(self):
        """Test webhook endpoints structure"""
        webhook_endpoints = ["/sms", "/ussd", "/delivery-report"]
        
        for endpoint in webhook_endpoints:
            try:
                # Test with empty POST (should handle gracefully)
                response = requests.post(f"{self.base_url}{endpoint}", 
                                       data={}, timeout=10)
                # Webhook should respond (might be error, but should not crash)
                if response.status_code in [200, 400, 422]:
                    self.log_test(f"Webhook {endpoint}", True, "Endpoint responsive")
                else:
                    self.log_test(f"Webhook {endpoint}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Webhook {endpoint}", False, f"Error: {str(e)}")
    
    def test_performance(self):
        """Test response times"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response_time < 2.0:
                self.log_test("Performance", True, f"Response time: {response_time:.2f}s")
            else:
                self.log_test("Performance", False, f"Slow response: {response_time:.2f}s")
        except Exception as e:
            self.log_test("Performance", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting MAMA-AI Production Test Suite")
        print("=" * 50)
        
        # Core functionality tests
        self.test_health_endpoint()
        self.test_database_connection()
        self.test_performance()
        
        # Communication tests
        self.test_sms_simulation()
        self.test_chat_interface()
        self.test_webhook_endpoints()
        
        # UI tests
        self.test_ui_endpoints()
        
        # Final report
        self.generate_report()
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 50)
        print("📊 FINAL TEST REPORT")
        print("=" * 50)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! Ready for production deployment!")
            print("✅ Your MAMA-AI system is production-ready")
        else:
            print(f"\n⚠️  {self.failed} tests failed. Please review before deployment.")
            print("❌ Fix issues before production deployment")
        
        # Save detailed report
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": self.passed,
                "failed": self.failed,
                "success_rate": success_rate,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results
        }
        
        with open("production_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: production_test_report.json")
        
        return self.failed == 0

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MAMA-AI Production Test Suite")
    parser.add_argument("--url", default="http://localhost:5000", 
                       help="Base URL to test (default: http://localhost:5000)")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick tests only")
    
    args = parser.parse_args()
    
    tester = ProductionTester(args.url)
    
    if args.quick:
        print("🏃 Running quick tests...")
        tester.test_health_endpoint()
        tester.test_database_connection()
        tester.generate_report()
    else:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
