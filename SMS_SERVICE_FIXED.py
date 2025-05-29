"""
FIXED SMS SERVICE - NO DUPLICATES, FULL AI RESPONSES
==================================================
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
    
    def handle_incoming_sms_simple(self, from_number, to_number, text, received_at):
        """SINGLE SMS handler - sends one complete AI response"""
        try:
            # Clean phone number
            clean_phone = self._clean_phone_number(from_number)
            
            # Log incoming SMS
            self._log_message(clean_phone, "SMS", "incoming", text)
            
            # Get or create user
            user = self._get_or_create_user(clean_phone)
            
            print(f"\n📱 INCOMING SMS:")
            print(f"📱 From: {clean_phone}")
            print(f"📝 Message: {text}")
            print(f"🕒 Received at: {received_at}")
            
            # Try to get AI response first
            ai_response = None
            try:
                print(f"\n🤖 PROCESSING WITH AI...")
                ai_response = self._process_sms_with_ai(text.strip(), user)
                if ai_response:
                    print(f"✅ AI Response generated: {ai_response}")
                else:
                    print(f"⚠️ AI returned empty response")
            except Exception as ai_error:
                print(f"❌ AI processing failed: {str(ai_error)}")
            
            # If AI failed, use fallback
            if not ai_response:
                print(f"\n🔄 USING FALLBACK RESPONSE...")
                ai_response = self._get_fallback_response(text.strip(), user)
            
            print(f"\n🤖 SENDING FINAL RESPONSE:")
            print(f"📝 Response: {ai_response}")
            print(f"📏 Length: {len(ai_response)} chars")
            
            # Send ONE response via DIRECT API
            sms_result = self.send_sms_direct_api(clean_phone, ai_response)
            
            if sms_result and sms_result.get("status") == "success":
                print(f"✅ SMS Response sent successfully!")
                # Log the outgoing message
                self._log_message(clean_phone, "SMS", "outgoing", ai_response)
                return {"status": "processed", "response_sent": True, "message": "SMS processed and response sent"}
            else:
                print(f"❌ Failed to send SMS response: {sms_result}")
                return {"status": "processed", "response_sent": False, "message": "SMS processed but response failed"}
                
        except Exception as e:
            print(f"❌ Error in SMS handler: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _process_sms_with_ai(self, text, user):
        """Process SMS using AI service with full response"""
        try:
            text_lower = text.lower().strip()
            
            # Handle STOP requests
            if any(keyword in text_lower for keyword in ['stop', 'acha', 'unsubscribe']):
                user.is_active = False
                db.session.commit()
                return self._get_ai_stop_response(user)
            
            # Create session ID
            session_id = f"sms_{user.phone_number}_{datetime.now().strftime('%Y%m%d_%H')}"
            
            # Add comprehensive context for AI
            context_message = f"""
SMS from user: {text}

User Context:
- Phone: {user.phone_number}
- Language: {user.preferred_language or 'English'}
- First time user: {'Yes' if not user.name else 'No'}

Instructions:
- Respond as MAMA-AI, the maternal health assistant
- Provide helpful, accurate medical information
- Keep responses conversational but informative
- If it's a greeting, provide a warm welcome
- For health questions, give detailed helpful advice
- Include emojis to make responses friendly
- IMPORTANT: Provide COMPLETE responses, don't truncate
- For pregnancy questions, give comprehensive guidance
- Always be supportive and understanding
"""
            
            # Get AI response
            ai_response = self.ai_service.chat_with_ai(
                user_message=context_message,
                user=user,
                session_id=session_id,
                channel='SMS'
            )
            
            # Ensure full response is returned
            if ai_response:
                print(f"🤖 Full AI Response Generated: {len(ai_response)} chars")
                return ai_response
            else:
                print(f"⚠️ AI returned empty response")
                return None
            
        except Exception as e:
            print(f"❌ Error processing SMS with AI: {str(e)}")
            return None
    
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
            
            headers = {
                'apiKey': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'username': self.username,
                'to': clean_phone,
                'message': message,
                'from': self.shortcode
            }
            
            # Send with SSL verification disabled
            response = requests.post(
                url, 
                headers=headers, 
                data=data, 
                verify=False,  # Bypass SSL verification
                timeout=30
            )
            
            print(f"\n📊 API Response:")
            print(f"   Status: {response.status_code}")
            print(f"   Body: {response.text}")
            
            if response.status_code == 201:
                print(f"✅ SMS sent successfully via direct API!")
                return {"status": "success", "response": response.text}
            else:
                print(f"❌ SMS sending failed: {response.status_code} - {response.text}")
                return {"status": "failed", "error": response.text}
            
        except Exception as e:
            print(f"❌ Error in direct API SMS: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _is_supported_sandbox_number(self, phone_number):
        """Check if phone number is supported in sandbox"""
        # Africa's Talking sandbox supports these test numbers
        supported_prefixes = ['+254711', '+254712', '+254713', '+254714', '+254715']
        return any(phone_number.startswith(prefix) for prefix in supported_prefixes)
    
    def _get_fallback_response(self, user_message, user):
        """Get fallback response based on message content"""
        user_message = user_message.lower()
        
        # Swahili greetings
        if any(word in user_message for word in ['habari', 'hujambo', 'mambo', 'salama']):
            return "Habari yako! Mimi ni MAMA-AI. Nipo hapa kukusaidia na maswali ya afya ya mama na mtoto. Uliza chochote! 🤱"
        
        # English greetings
        if any(word in user_message for word in ['hello', 'hi', 'hey', 'good', 'start']):
            return "Hello! I'm MAMA-AI, your maternal health assistant. I'm here to help with pregnancy and maternal health questions. Ask me anything! 👋"
        
        # Health-related fallbacks
        if any(word in user_message for word in ['sick', 'pain', 'health', 'hurt']):
            return "I understand you have health concerns. For emergencies, please visit a hospital immediately. For non-urgent health advice, I can help guide you. What specific symptoms are you experiencing? 🏥"
        
        # Pregnancy-related fallbacks  
        if any(word in user_message for word in ['pregnancy', 'pregnant', 'baby', 'birth']):
            return "I'm here to help with pregnancy questions! Pregnancy is when a baby grows inside the mother's womb for about 9 months. Regular prenatal care, proper nutrition, and rest are very important. What specific pregnancy question do you have? 👶"
        
        # Default response
        return "Hello! I'm MAMA-AI, your maternal health assistant. I help with pregnancy, prenatal care, and women's health questions. Please feel free to ask me anything about maternal health. For emergencies, contact a doctor immediately! 💙"
    
    def _get_ai_stop_response(self, user):
        """Get AI-powered unsubscribe confirmation"""
        try:
            if user.preferred_language == 'sw':
                return "Umejitoa MAMA-AI. Andika START kwa 15629 kurudi. Dharura: enda hospitali. 🤱"
            else:
                return "Unsubscribed from MAMA-AI. Text START to 15629 to resubscribe. Emergencies: go to hospital. 🤱"
        except:
            return "Unsubscribed from MAMA-AI. Text START to 15629 to resubscribe. Emergencies: go to hospital. 🤱"
    
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
        """Log message to database - FIXED timestamp issue"""
        try:
            message_log = MessageLog(
                phone_number=phone_number,
                message_type=msg_type,
                direction=direction,
                content=content
                # created_at is automatically set by the model
            )
            db.session.add(message_log)
            db.session.commit()
            print(f"📝 Logged {direction} {msg_type}: {content[:50]}...")
        except Exception as e:
            print(f"❌ Error logging message: {str(e)}")
            db.session.rollback()
    
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
