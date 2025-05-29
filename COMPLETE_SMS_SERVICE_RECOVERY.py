"""
COMPLETE SMS SERVICE RECOVERY FILE
=================================
Copy this entire content to replace your SMS service file.
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

class SMSService:
    def __init__(self):
        # Initialize Africa's Talking
        username = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
        api_key = os.getenv('AFRICASTALKING_API_KEY')
        
        if api_key:
            africastalking.initialize(username, api_key)
        
        self.sms = africastalking.SMS
        self.ai_service = AIService()
        self.shortcode = '15629'  # Your Africa's Talking shortcode
        self.username = username
        self.api_key = api_key
    
    def send_sms_direct_api(self, phone_number, message, sender_id=None):
        """Send SMS using direct API call to bypass SSL issues"""
        try:
            # Clean phone number
            clean_phone = self._clean_phone_number(phone_number)
            
            # Check if it's a supported sandbox number
            if not self._is_supported_sandbox_number(clean_phone):
                print(f"⚠️ Converting unsupported number {clean_phone} to test number")
                clean_phone = "+254712345678"  # Use Kenya test number
            
            print(f"\n🤖 SENDING SMS via DIRECT API:")
            print(f"📱 To: {clean_phone}")
            print(f"📝 Message: {message}")
            print(f"📏 Length: {len(message)} chars")
            
            # API details
            url = "https://api.sandbox.africastalking.com/version1/messaging"
            
            # Headers
            headers = {
                'apikey': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Data
            data = {
                'username': self.username,
                'to': clean_phone,
                'message': message
            }
            
            # Make request with SSL verification disabled
            response = requests.post(
                url, 
                headers=headers, 
                data=data, 
                verify=False,  # Disable SSL verification
                timeout=30
            )
            
            print(f"\n📊 API Response:")
            print(f"   Status: {response.status_code}")
            print(f"   Body: {response.text}")
            
            # Check if successful
            if response.status_code == 201 and "Success" in response.text:
                print("✅ SMS sent successfully via direct API!")
                self._log_message(clean_phone, "SMS", "outgoing", message)
                return {"status": "success", "response": response.text}
            else:
                print(f"❌ SMS failed - Status: {response.status_code}")
                return {"status": "failed", "response": response.text}
                
        except Exception as e:
            print(f"❌ Direct API SMS failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _is_supported_sandbox_number(self, phone_number):
        """Check if phone number is supported in Africa's Talking sandbox"""
        supported_patterns = [
            '+254',  # Kenya
            '+256',  # Uganda  
            '+255',  # Tanzania
            '+250',  # Rwanda
            '+211',  # South Sudan
            '+237',  # Cameroon
        ]
        
        for pattern in supported_patterns:
            if phone_number.startswith(pattern):
                return True
        return False
    
    def handle_incoming_sms_simple(self, from_number, to_number, text, received_at):
        """Simplified SMS handler with immediate fallback responses"""
        try:
            # Clean phone number
            clean_phone = self._clean_phone_number(from_number)
            
            # Log incoming SMS
            self._log_message(clean_phone, "SMS", "incoming", text)
            
            # Get or create user
            user = self._get_or_create_user(clean_phone)
            
            print(f"\n📱 INCOMING SMS (SIMPLE MODE):")
            print(f"📱 From: {clean_phone}")
            print(f"📝 Message: {text}")
            print(f"🕒 Received at: {received_at}")
            
            # Get immediate fallback response (skip AI due to rate limits)
            response = self._get_fallback_response(text.strip(), user)
            
            print(f"\n🤖 SENDING FALLBACK RESPONSE:")
            print(f"📝 Response: {response}")
            
            # Send response SMS back to user using DIRECT API
            sms_result = self.send_sms_direct_api(clean_phone, response)
            
            if sms_result and sms_result.get("status") == "success":
                print(f"✅ SMS Response sent successfully!")
                return {"status": "processed", "response_sent": True, "message": "SMS processed and response sent"}
            else:
                print(f"❌ Failed to send SMS response: {sms_result}")
                return {"status": "processed", "response_sent": False, "message": "SMS processed but response failed"}
                
        except Exception as e:
            print(f"❌ Error in simple SMS handler: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _get_fallback_response(self, user_message, user):
        """Get a safe fallback response when AI is filtered or fails"""
        user_message = user_message.lower()
        
        # Swahili greetings
        if any(word in user_message for word in ['habari', 'hujambo', 'mambo', 'salama']):
            return "Habari yako! Mimi ni MAMA-AI. Nipo hapa kukusaidia na maswali ya afya ya mama na mtoto. Uliza chochote! 🤱"
        
        # English greetings
        if any(word in user_message for word in ['hello', 'hi', 'hey', 'good', 'start']):
            return "Hello! I'm MAMA-AI, your maternal health assistant. I'm here to help with pregnancy and maternal health questions. Ask me anything! 👋"
        
        # Health-related fallbacks
        if any(word in user_message for word in ['mgonjwa', 'sick', 'pain', 'dawa', 'health', 'maumivu']):
            return "I understand you have health concerns. For emergencies, please visit a hospital immediately. For health advice, consult with a doctor. 🏥"
        
        # Pregnancy-related fallbacks  
        if any(word in user_message for word in ['mimba', 'pregnancy', 'pregnant', 'baby', 'mtoto']):
            return "For pregnancy-related questions, I recommend consulting with a healthcare provider. Regular prenatal care is important for you and your baby! 👶"
        
        # Default response
        return "Hello! I'm MAMA-AI. I help with maternal health questions. Please ask me about pregnancy, prenatal care, or women's health. For emergencies, contact a doctor immediately! 💙"
    
    def _clean_phone_number(self, phone_number):
        """Clean and format phone number"""
        if not phone_number:
            return phone_number
        
        # Remove spaces and special characters
        clean = phone_number.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Ensure it starts with +
        if not clean.startswith('+'):
            if clean.startswith('0'):
                # Assume it's a local number (Kenya in this case)
                clean = '+254' + clean[1:]
            else:
                clean = '+' + clean
        
        return clean
    
    def _log_message(self, phone_number, message_type, direction, content):
        """Log message to database"""
        try:
            message_log = MessageLog(
                phone_number=phone_number,
                message_type=message_type,
                direction=direction,
                content=content,
                timestamp=datetime.utcnow()
            )
            db.session.add(message_log)
            db.session.commit()
            print(f"📝 Message logged: {direction} {message_type} to/from {phone_number}")
        except Exception as e:
            print(f"❌ Error logging message: {e}")
    
    def _get_or_create_user(self, phone_number):
        """Get or create user from phone number"""
        try:
            user = User.query.filter_by(phone_number=phone_number).first()
            if not user:
                user = User(
                    phone_number=phone_number,
                    preferred_language='English',
                    is_active=True
                )
                db.session.add(user)
                db.session.commit()
                print(f"👤 Created new user: {phone_number}")
            return user
        except Exception as e:
            print(f"❌ Error getting/creating user: {e}")
            return None
