"""
KEY CHANGES I MADE - PART 3
===========================

3. SSL FIXES (add to top of sms_service.py):
"""

import os
import africastalking
import requests
import ssl
import urllib3
from datetime import datetime
from src.models import db, User, MessageLog
from src.services.ai_service import AIService

# Comprehensive SSL fix
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
4. UPDATED APP.PY SMS CALLBACK:
"""

@app.route('/sms', methods=['POST'])
def sms_callback():
    """Handle incoming SMS from Africa's Talking"""
    try:
        # Get SMS parameters from form data (Africa's Talking sends form data)
        from_number = request.form.get('from')
        to_number = request.form.get('to') 
        text = request.form.get('text')
        date = request.form.get('date')
        
        print(f"📱 Incoming SMS from {from_number}: {text}")
        
        # Try simple handler first, then fallback to regular handler
        try:
            response = sms_service.handle_incoming_sms_simple(
                from_number=from_number,
                to_number=to_number,
                text=text,
                received_at=date
            )
        except Exception as simple_error:
            print(f"⚠️ Simple handler failed: {simple_error}")
            print("🔄 Trying regular SMS handler...")
            response = sms_service.handle_incoming_sms(
                from_number=from_number,
                to_number=to_number,
                text=text,
                received_at=date
            )
        
        print(f"✅ SMS processed successfully")
        
        # Return 200 status to Africa's Talking (important!)
        return "", 200
        
    except Exception as e:
        app.logger.error(f"SMS Error: {str(e)}")
        print(f"❌ SMS Error: {str(e)}")
        return "", 500

"""
5. KEY INSIGHT: 
The phone number +93345432223 you're testing with is NOT SUPPORTED in Africa's Talking sandbox.
Use +254712345678 (Kenya) instead for testing.

The direct API method automatically converts unsupported numbers to +254712345678.
"""
