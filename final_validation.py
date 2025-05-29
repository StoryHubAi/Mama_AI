#!/usr/bin/env python3
"""
MAMA-AI Final Validation Script
Comprehensive system validation after deployment
"""

import sys
import os
import requests
import json
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ValidationResult:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []

    def pass_test(self, test_name):
        print(f"✅ {test_name}")
        self.tests_passed += 1

    def fail_test(self, test_name, error):
        print(f"❌ {test_name}: {error}")
        self.tests_failed += 1
        self.errors.append(f"{test_name}: {error}")

    def summary(self):
        total = self.tests_passed + self.tests_failed
        print(f"\n📊 Validation Summary:")
        print(f"   Total tests: {total}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("🎉 All tests passed! MAMA-AI is ready for production.")
        else:
            print("⚠️ Some tests failed. Review errors above.")
            
        return self.tests_failed == 0

def validate_environment(result):
    """Validate environment variables"""
    print("\n🔧 Validating Environment Configuration...")
    
    required_vars = [
        'AFRICASTALKING_USERNAME',
        'AFRICASTALKING_API_KEY', 
        'AFRICASTALKING_SHORTCODE',
        'GITHUB_TOKEN',
        'MYSQL_HOST',
        'MYSQL_USER',
        'MYSQL_PASSWORD',
        'MYSQL_DATABASE'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value and value != 'test_api_key_for_development':
            result.pass_test(f"Environment variable {var}")
        else:
            result.fail_test(f"Environment variable {var}", "Missing or default value")

def validate_database(result):
    """Validate database connection and tables"""
    print("\n🗄️ Validating Database...")
    
    try:
        # Test MySQL connection
        host = os.getenv('MYSQL_HOST', 'localhost')
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', '8498')
        database = os.getenv('MYSQL_DATABASE', 'mama_ai')
        
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            result.pass_test("MySQL database connection")
            
            cursor = connection.cursor()
            
            # Check if tables exist
            required_tables = ['users', 'pregnancies', 'appointments', 'reminders', 'message_logs', 'conversations']
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            
            for table in required_tables:
                if table in existing_tables:
                    result.pass_test(f"Database table '{table}'")
                else:
                    result.fail_test(f"Database table '{table}'", "Table does not exist")
            
            cursor.close()
            connection.close()
        else:
            result.fail_test("MySQL database connection", "Could not connect")
            
    except Exception as e:
        result.fail_test("Database validation", str(e))

def validate_flask_app(result):
    """Validate Flask application endpoints"""
    print("\n🌐 Validating Flask Application...")
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            result.pass_test("Health endpoint")
        else:
            result.fail_test("Health endpoint", f"Status code: {response.status_code}")
    except Exception as e:
        result.fail_test("Health endpoint", str(e))
    
    # Test SMS endpoint
    try:
        sms_data = {
            'to': '15629',
            'from': '+254700123456',
            'text': 'Hello MAMA-AI test',
            'date': datetime.now().isoformat(),
            'id': 'validation_test',
            'linkId': 'validation_link'
        }
        
        response = requests.post(f"{base_url}/sms", data=sms_data, timeout=30)
        if response.status_code == 200:
            result.pass_test("SMS endpoint")
        else:
            result.fail_test("SMS endpoint", f"Status code: {response.status_code}")
    except Exception as e:
        result.fail_test("SMS endpoint", str(e))
    
    # Test USSD endpoint
    try:
        ussd_data = {
            'sessionId': 'validation_session',
            'serviceCode': '*123#',
            'phoneNumber': '+254700123456',
            'text': ''
        }
        
        response = requests.post(f"{base_url}/ussd", data=ussd_data, timeout=30)
        if response.status_code == 200 and "Welcome to MAMA-AI" in response.text:
            result.pass_test("USSD endpoint")
        else:
            result.fail_test("USSD endpoint", f"Unexpected response: {response.text[:100]}")
    except Exception as e:
        result.fail_test("USSD endpoint", str(e))

def validate_ai_service(result):
    """Validate AI service integration"""
    print("\n🤖 Validating AI Service...")
    
    try:
        chat_data = {
            'message': 'What vitamins should I take during pregnancy?',
            'phone_number': '+254700123456',
            'language': 'en'
        }
        
        response = requests.post(
            "http://localhost:5000/chat",
            json=chat_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and len(data['response']) > 50:
                result.pass_test("AI chat endpoint")
            else:
                result.fail_test("AI chat endpoint", "Response too short or missing")
        else:
            result.fail_test("AI chat endpoint", f"Status code: {response.status_code}")
            
    except Exception as e:
        result.fail_test("AI chat endpoint", str(e))

def validate_dependencies(result):
    """Validate Python dependencies"""
    print("\n📦 Validating Dependencies...")
    
    required_packages = [
        'flask',
        'flask_sqlalchemy', 
        'africastalking',
        'azure.ai.inference',
        'mysql.connector',
        'pymysql',
        'python_dotenv',
        'requests'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            result.pass_test(f"Package {package}")
        except ImportError:
            result.fail_test(f"Package {package}", "Not installed")

def main():
    """Run comprehensive validation"""
    print("🧪 MAMA-AI Comprehensive Validation")
    print("=" * 50)
    
    result = ValidationResult()
    
    # Run all validations
    validate_dependencies(result)
    validate_environment(result)
    validate_database(result)
    validate_flask_app(result)
    validate_ai_service(result)
    
    # Show summary
    success = result.summary()
    
    if success:
        print("\n🚀 MAMA-AI validation completed successfully!")
        print("\n✅ System is ready for:")
        print("   • SMS interactions via Africa's Talking")
        print("   • USSD menu navigation")
        print("   • AI-powered maternal health assistance")
        print("   • Emergency detection and response")
        print("   • Bilingual support (English/Kiswahili)")
        print("\n📞 Configure webhook URLs in Africa's Talking dashboard:")
        print("   SMS: https://your-domain.com/sms")
        print("   USSD: https://your-domain.com/ussd")
    else:
        print("\n❌ Validation failed. Please fix the issues above before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
