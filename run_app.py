#!/usr/bin/env python3
"""
Simple Flask App Runner for MAMA-AI
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run the Flask application"""
    try:
        print("🚀 Starting MAMA-AI Flask Application...")
        print("=" * 50)
        
        # Import and run the app
        from app import app
        
        # Print configuration info
        print(f"✅ Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
        print(f"✅ Secret Key: {'Configured' if app.config.get('SECRET_KEY') else 'Not configured'}")
        print(f"✅ Africa's Talking: {'Configured' if os.getenv('AFRICASTALKING_API_KEY') else 'Not configured'}")
        print(f"✅ GitHub Token: {'Configured' if os.getenv('GITHUB_TOKEN') else 'Not configured'}")
        
        print("\n🌟 MAMA-AI is starting...")
        print("📱 SMS webhook: http://localhost:5000/sms")
        print("📞 USSD webhook: http://localhost:5000/ussd")
        print("🤖 AI chat: http://localhost:5000/chat")
        print("❤️ Health check: http://localhost:5000/health")
        print("\n🚀 Server starting on http://localhost:5000")
        print("=" * 50)
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid issues
        )
        
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
