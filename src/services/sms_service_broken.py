import os
import ssl
import logging
import requests
import africastalking
from datetime import datetime
from src.models import db, User, MessageLog
from src.services.ai_service import AIService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix SSL issues for Africa's Talking sandbox - comprehensive fix
try:
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    # Also disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass

class SMSService:
    def __init__(self):
        # Initialize Africa's Talking properly
        username = os.getenv('AFRICASTALKING_USERNAME', 'sandbox')
        api_key = os.getenv('AFRICASTALKING_API_KEY')
        
        print(f"🔑 Initializing SMS Service with:")
        print(f"   Username: {username}")
        print(f"   API Key: {api_key[:20]}..." if api_key else "   API Key: None")
        
        logger.info(f"SMS Service initializing - Username: {username}, API Key: {'Present' if api_key else 'Missing'}")
        
        if api_key and api_key != 'test_api_key_for_development':
            africastalking.initialize(username, api_key)
            print(f"✅ SMS Service initialized successfully")
            logger.info("SMS Service initialized successfully")
        else:
            print("⚠️ SMS Service: No valid API key found")
            logger.warning("SMS Service: No valid API key found")
        
        self.sms = africastalking.SMS
        self.ai_service = AIService()
        self.shortcode = os.getenv('AFRICASTALKING_SHORTCODE', '15629')

    def send_sms(self, phone_number, message, sender_id=None):
        """Send SMS using Africa's Talking - Following the official documentation"""
        try:
            # Clean phone number to international format
            clean_phone = self._clean_phone_number(phone_number)
            
            # Use your shortcode as sender (this is the AI sending back)
            if not sender_id:
                sender_id = self.shortcode
            
            # **DISPLAY FULL RESPONSE** - Show complete message and details
            print(f"\n🤖 AI RESPONSE BEING SENT:")
            print(f"📱 To: {clean_phone}")
            print(f"🏷️ From: {sender_id} (MAMA-AI)")
            print(f"📝 Full Message: {message}")  # Show FULL message, not truncated
            print(f"📏 Message Length: {len(message)} characters")
            
            logger.info(f"AI sending SMS to {clean_phone} from {sender_id}")
            logger.info(f"Full message content: {message}")
            
            # Send SMS using Africa's Talking format from documentation
            # Format: sms.send(message, recipients, sender_id)
            response = self.sms.send(
                message=message,
                recipients=[clean_phone],  # Must be a list
                sender_id=sender_id        # Your shortcode
            )
            
            # Log the outgoing SMS
            self._log_message(clean_phone, "SMS", "outgoing", message)
            
            print(f"\n✅ SMS SENT SUCCESSFULLY!")
            print(f"📊 Africa's Talking Response: {response}")
            print(f"🔄 Two-way conversation: User → AI → User ✓")
            
            logger.info(f"SMS sent successfully. AT Response: {response}")
            return response
            
        except Exception as e:
            print(f"\n❌ SMS SENDING FAILED:")
            print(f"   Error: {str(e)}")
            print(f"   To: {phone_number}")
            print(f"   Message: {message}")
            
            # Try alternative format from documentation
            try:
                print("\n🔄 RETRYING with alternative format...")
                # Try without sender_id first
                response = self.sms.send(message, [clean_phone])
                print(f"✅ Retry successful without sender_id: {response}")
                self._log_message(clean_phone, "SMS", "outgoing", message)
                return response
            except Exception as e2:
                print(f"❌ Retry also failed: {str(e2)}")
                logger.error(f"SMS sending failed completely: {str(e2)}")
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
            
            # Use shortcode as sender
            if not sender_id:
                sender_id = self.shortcode
            
            print(f"\n🤖 SENDING SMS via DIRECT API:")
            print(f"📱 To: {clean_phone}")
            print(f"🏷️ From: {sender_id}")
            print(f"📝 Message: {message}")
            print(f"📏 Length: {len(message)} chars")
            
            # API details
            username = self.username
            api_key = self.api_key
            url = "https://api.sandbox.africastalking.com/version1/messaging"
            
            # Headers
            headers = {
                'apikey': api_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Data
            data = {
                'username': username,
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
            logger.error(f"Direct API SMS error: {e}")
            return {"status": "error", "error": str(e)}
    
    def handle_incoming_sms(self, from_number, to_number, text, received_at):
        """Handle incoming SMS messages with AI-ONLY responses"""
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
            
            # Process ALL messages with AI (no special commands except STOP)
            ai_response = self._process_sms_with_ai(text.strip(), user)
            
            if ai_response:
                print(f"\n🤖 AI GENERATED RESPONSE:")
                print(f"📝 Full AI Response: {ai_response}")
                  # Send response SMS back to user (AI becomes the sender)
                sms_result = self.send_sms(clean_phone, ai_response)
                
                if sms_result:
                    print(f"🤖 AI Response sent successfully!")
                    return {"status": "processed", "response_sent": True, "message": "SMS processed and response sent"}
                else:
                    print(f"❌ Failed to send SMS response")
                    return {"status": "processed", "response_sent": False, "message": "SMS processed but response failed"}
            else:
                print(f"❌ No AI response generated")
                return {"status": "error", "response_sent": False, "message": "No AI response generated"}
        except Exception as e:
            print(f"❌ Error handling incoming SMS: {str(e)}")
            return {"status": "error", "message": str(e)}

    def handle_incoming_sms_simple(self, from_number, to_number, text, received_at):
        """Simplified SMS handler with immediate fallback responses - for testing"""
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
            print(f"📝 Response: {response}")            # Send response SMS back to user using DIRECT API
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
            
            # Simplified context for AI to avoid content filtering
            simple_context = f"User sent: {text}"
            
            print(f"🤖 Sending to AI: {simple_context}")
            
            try:
                ai_response = self.ai_service.chat_with_ai(
                    simple_context,
                    user,
                    session_id,
                    'SMS'
                )
                
                print(f"🤖 AI Response received: {ai_response}")
                
                # If AI response is blocked, provide fallback
                if not ai_response or "content_filter" in str(ai_response).lower():
                    print("🛡️ AI response filtered, using fallback")
                    ai_response = self._get_fallback_response(text, user)
                
                return ai_response
                
            except Exception as ai_error:
                print(f"❌ AI Service Error: {str(ai_error)}")
                
                # Check for rate limit specifically
                if "429" in str(ai_error) or "rate" in str(ai_error).lower():
                    print("⏰ Rate limit hit, using fallback response")
                
                # Always return fallback when AI fails
                fallback_response = self._get_fallback_response(text, user)
                print(f"🔄 Using fallback response: {fallback_response}")
                return fallback_response
              except Exception as e:
            print(f"❌ Error processing SMS with AI: {str(e)}")
            # Return fallback response
            fallback_response = self._get_fallback_response(text, user)
            print(f"🔄 Exception fallback response: {fallback_response}")
            return fallback_response

    def _get_fallback_response(self, user_message, user):
        """Get a safe fallback response when AI is filtered or fails"""
        user_message = user_message.lower()
        
        # Swahili greetings
        if any(word in user_message for word in ['habari', 'hujambo', 'mambo', 'salama']):
            return "Habari yako! Mimi ni MAMA-AI. Nipo hapa kukusaidia na maswali ya afya ya mama na mtoto. Uliza chochote! 🤱"
        
        # English greetings
        if any(word in user_message for word in ['hello', 'hi', 'hey', 'good']):
            return "Hello! I'm MAMA-AI, your maternal health assistant. I'm here to help with pregnancy and maternal health questions. Ask me anything! 👋"
        
        # Health-related fallbacks
        if any(word in user_message for word in ['mgonjwa', 'sick', 'pain', 'dawa', 'health', 'maumivu']):
            return "Nimesikia una hali mbaya. Kama ni dharura, enda hospitali mara moja. Kwa ushauri wa afya, ongea na daktari. 🏥"
        
        # Pregnancy-related fallbacks  
        if any(word in user_message for word in ['mimba', 'pregnant', 'baby', 'mtoto', 'ujauzito']):
            return "Kwa habari za mimba na mtoto, ni muhimu kutembelea kliniki mara kwa mara. Usisite kuuliza ikiwa una maswali! 🤱"
        
        # Help requests
        if any(word in user_message for word in ['help', 'msaada', 'saidia']):
            return "Mimi ni MAMA-AI! Naweza kukusaidia na: 1)Maswali ya mimba 2)Afya ya mama 3)Utunzaji wa mtoto 4)Chakula cha afya. Uliza! �"
            
        # Default contextual response based on the message
        return f"Nimepokea ujumbe wako: '{user_message[:30]}...' Mimi ni MAMA-AI, msaidizi wa afya ya mama. Uliza swali fulani! 🤱"

    def _get_ai_stop_response(self, user):
        """Get AI-powered unsubscribe confirmation"""
        try:
            if user.preferred_language == 'sw':
                return "Umejitoa MAMA-AI. Andika START kwa 15629 kurudi. Dharura: enda hospitali. 🤱"
            else:
                return "Unsubscribed from MAMA-AI. Text START to 15629 to resubscribe. Emergencies: go to hospital. 🤱"
        except:
            return "Unsubscribed from MAMA-AI. Text START to 15629 to resubscribe. 🤱"

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
                content=content
            )
            db.session.add(message_log)
            db.session.commit()
            print(f"📝 Message logged: {direction} {msg_type} to/from {phone_number}")
        except Exception as e:
            print(f"❌ Error logging message: {str(e)}")
            db.session.rollback()
