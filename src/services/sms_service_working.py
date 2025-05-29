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
    
    def send_sms(self, phone_number, message, sender_id=None):
        """Send SMS using Africa's Talking"""
        try:
            # Clean phone number
            clean_phone = self._clean_phone_number(phone_number)
            
            # Use your shortcode
            if not sender_id:
                sender_id = self.shortcode
            
            # Send SMS
            response = self.sms.send(
                message=message,
                recipients=[clean_phone],
                sender_id=sender_id
            )
            
            # Log the SMS
            self._log_message(clean_phone, "SMS", "outgoing", message)
            
            print(f"✅ SMS sent to {clean_phone}: {message[:50]}...")
            return response
            
        except Exception as e:
            print(f"❌ Error sending SMS: {str(e)}")
            return None
    
    def handle_incoming_sms(self, from_number, to_number, text, received_at):
        """Handle incoming SMS messages with AI-ONLY responses"""
        try:
            # Clean phone number
            clean_phone = self._clean_phone_number(from_number)
            
            # Log incoming SMS
            self._log_message(clean_phone, "SMS", "incoming", text)
            
            # Get or create user
            user = self._get_or_create_user(clean_phone)
            
            print(f"📱 Received SMS from {clean_phone}: {text}")
            
            # Process ALL messages with AI (no special commands except STOP)
            response = self._process_sms_with_ai(text.strip(), user)
            
            if response:
                # Send response SMS
                self.send_sms(clean_phone, response)
                print(f"🤖 AI Response sent: {response[:50]}...")
            
            return {"status": "processed", "response_sent": bool(response)}
            
        except Exception as e:
            print(f"❌ Error handling incoming SMS: {str(e)}")
            return {"status": "error", "message": str(e)}
    
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
    
    def _process_sms_with_ai(self, text, user):
        """Process SMS using AI service - EVERYTHING goes to AI"""
        try:
            text_lower = text.lower().strip()
            
            # Only handle STOP for legal compliance
            if any(keyword in text_lower for keyword in ['stop', 'acha', 'unsubscribe']):
                user.is_active = False
                db.session.commit()
                return self._get_ai_stop_response(user)
            
            # EVERYTHING ELSE goes to AI - including START, HELP, questions, anything
            session_id = f"sms_{user.phone_number}_{datetime.now().strftime('%Y%m%d_%H')}"
            
            # Add context to the message for AI
            context_message = f"""
SMS from user: {text}

Context:
- User name: {user.name or 'Not provided'}
- Phone: {user.phone_number}
- Language preference: {user.preferred_language or 'English'}
- First time user: {'Yes' if not user.name else 'No'}

Instructions:
- If this looks like a greeting/start request, provide a warm welcome and explain how to use the service
- If this is a health question, provide helpful medical advice
- If they're asking for help/menu, explain they can ask any health questions directly
- Always respond as MAMA-AI, the maternal health assistant
- Keep responses under 160 characters when possible for SMS
- Use appropriate language (English or Kiswahili based on their preference)
"""
            
            ai_response = self.ai_service.chat_with_ai(
                user_message=context_message,
                user=user,
                session_id=session_id,
                channel='SMS'
            )
            
            return ai_response
            
        except Exception as e:
            print(f"❌ Error processing SMS with AI: {str(e)}")
            # Last resort - try to get AI error response
            try:
                return self.ai_service._get_error_response(user.preferred_language or 'en', user)
            except:
                return "MAMA-AI error. Text any health question to try again. 🤱"
    
    def _get_ai_stop_response(self, user):
        """Get AI-powered unsubscribe confirmation"""
        try:
            stop_prompt = f"""
User {user.name or 'Mama'} wants to unsubscribe from MAMA-AI SMS service.
Generate a polite goodbye message in {'Kiswahili' if user.preferred_language == 'sw' else 'English'}.

Include:
- Confirmation they're unsubscribed
- How to resubscribe (text START to 15629)
- Emergency reminder (go to hospital for emergencies)
- Warm goodbye

Keep under 160 characters.
"""
            return self.ai_service._get_ai_response_direct(stop_prompt, user, user.preferred_language or 'en')
        except:
            # Legal compliance fallback
            if user.preferred_language == 'sw':
                return "Umejitoa MAMA-AI. Andika START kwa 15629 kurudi. Dharura: enda hospitali. 🤱"
            else:
                return "Unsubscribed from MAMA-AI. Text START to 15629 to resubscribe. Emergencies: go to hospital. 🤱"
    
    def _get_or_create_user(self, phone_number):
        """Get or create user from database"""
        try:
            clean_phone = self._clean_phone_number(phone_number)
            user = User.query.filter_by(phone_number=clean_phone).first()
            
            if not user:
                user = User(
                    phone_number=clean_phone,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    preferred_language='en'  # Default, AI will detect and adjust
                )
                db.session.add(user)
                db.session.commit()
                print(f"✅ New user created: {clean_phone}")
            
            return user
            
        except Exception as e:
            print(f"❌ Error getting/creating user: {str(e)}")
            db.session.rollback()
            raise
    
    def _clean_phone_number(self, phone_number):
        """Clean and format phone number"""
        if not phone_number:
            return None
        
        # Remove any non-digit characters
        clean = ''.join(filter(str.isdigit, phone_number))
        
        # Handle Kenyan numbers
        if clean.startswith('0'):
            clean = '254' + clean[1:]
        elif clean.startswith('254'):
            pass  # Already correct
        elif clean.startswith('7') and len(clean) == 9:
            clean = '254' + clean
        
        return '+' + clean
    
    def _log_message(self, phone_number, msg_type, direction, content):
        """Log message to database"""
        try:
            message_log = MessageLog(
                phone_number=phone_number,
                message_type=msg_type,
                direction=direction,
                content=content,
                timestamp=datetime.utcnow()
            )
            db.session.add(message_log)
            db.session.commit()
        except Exception as e:
            print(f"❌ Error logging message: {str(e)}")
            db.session.rollback()
    
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
