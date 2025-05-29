#!/usr/bin/env python3
"""
MAMA-AI Startup Script
Initializes database and starts the Flask application
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask-sqlalchemy',
        'africastalking',
        'azure-ai-inference',
        'mysql-connector-python',
        'pymysql',
        'python-dotenv'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n⚠️ Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All dependencies available")
    return True

def setup_database():
    """Initialize the database"""
    print("\n🗄️ Setting up database...")
    
    try:
        # Run database initialization
        result = subprocess.run([
            sys.executable, 
            "init_db_mysql.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database setup completed")
            return True
        else:
            print(f"❌ Database setup failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        return False

def start_flask_app():
    """Start the Flask application"""
    print("\n🚀 Starting MAMA-AI Flask Application...")
    print("=" * 50)
    
    try:
        # Set environment variables
        os.environ['FLASK_APP'] = 'app.py'
        os.environ['FLASK_ENV'] = 'development'
        
        # Start Flask app
        print("🌐 Starting server at http://localhost:5000")
        print("📱 SMS webhook: http://localhost:5000/sms")
        print("📞 USSD webhook: http://localhost:5000/ussd")
        print("🤖 AI Chat: http://localhost:5000/chat")
        print("\n🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Import and run the app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n\n👋 MAMA-AI server stopped")
    except Exception as e:
        print(f"❌ Error starting Flask app: {str(e)}")

def show_usage_info():
    """Show usage information"""
    print("\n📖 MAMA-AI Usage Information")
    print("=" * 40)
    print("SMS Commands:")
    print("• Send any message to get AI response")
    print("• 'HELP' - Get help menu")
    print("• 'START' - Subscribe to service")
    print("• 'STOP' - Unsubscribe from service")
    print()
    print("USSD Menu (*123#):")
    print("• 1. Pregnancy Tips (Mapendekezo ya Ujauzito)")
    print("• 2. Check Symptoms (Angalia Dalili)")
    print("• 3. My Appointments (Miadi Yangu)")
    print("• 4. Emergency Help (Msaada wa Haraka)")
    print("• 5. Language/Lugha (EN/SW)")
    print()
    print("API Endpoints:")
    print("• POST /sms - SMS webhook")
    print("• POST /ussd - USSD webhook")
    print("• POST /chat - AI chat endpoint")
    print("• POST /test-sms - Test SMS sending")
    print()
    print("Features:")
    print("🤖 AI-powered responses using GitHub models")
    print("🌍 Bilingual support (English & Kiswahili)")
    print("🚨 Emergency detection and escalation")
    print("💬 Conversation history storage")
    print("📱 SMS and USSD integration")
    print("🏥 Maternal health guidance")
    print()

def main():
    """Main startup function"""
    print("🤱 MAMA-AI Startup Script")
    print("AI-Powered Maternal Health Assistant")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if this is first run
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        print("🔧 First-time setup mode")
        
        # Check dependencies
        if not check_dependencies():
            print("❌ Please install missing dependencies first")
            return
        
        # Setup database
        if not setup_database():
            print("❌ Database setup failed")
            return
        
        print("✅ Initialization complete!")
        print("Run 'python startup.py' to start the server")
        return
    
    # Show usage info
    show_usage_info()
    
    # Start the application
    start_flask_app()

if __name__ == "__main__":
    main()
