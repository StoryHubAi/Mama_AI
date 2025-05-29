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

# Fix SSL issues for Africa's Talking sandbox - more comprehensive fix
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
        self.shortcode = os.getenv('AFRICASTALKING_SHORTCODE', '15629')  # Your Africa's Talking shortcode
    
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
            print(f"� Two-way conversation: User → AI → User ✓")
            
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
            ai_response = self._process_sms_with_ai(text.strip(), user)
            
            if ai_response:
                # Send response SMS back to user
                sms_result = self.send_sms(clean_phone, ai_response)
                
                if sms_result:
                    print(f"🤖 AI Response sent successfully: {ai_response[:50]}...")
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
- If this looks like a greeting/sHey, Cortana. Hey, Cortana. Who are? This one at the top. This is another one. So when you. I just clicked the one on the top to achieve this. 0 pressure. Machine. Something. OK different people. Hey, Cortana capital letter A. Is that OK? It's totally capital. Hey, Cortana. Hey, Cortana. But but. 384. 57. 1000, 7000. And it's crazy, but. SMS to. It's OK to be the United Party positive. Access. To a new that's in a that's in a new way. Hey. Cortana. Hey, Cortana. Hello. Pressure. Play. I think I call master. Very nice. To ensure you capture the details. tart request, provide a warm welcome and explain how to use the service
- If this is a health question, provide helpful medical advice
- If they're asking for help/menu, explain they can ask any health questions directly
- Always respond as MAMA-AI, the maternal health assistant
- Keep responses under 160 characters when possible for SMS
- Use appropriate language (English or Kiswahili based on their preference)
"""
            
            ai_response = self.ai_service.chat_with_ai(
                context_message,
                user,
                session_id,
                'SMS'
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
                content=content
            )
            db.session.add(message_log)
            db.session.commit()
        except Exception as e:
            print(f"❌ Error logging message: {str(e)}")
            db.session.rollback()
