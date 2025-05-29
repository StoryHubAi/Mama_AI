import os
import africastalking
from datetime import datetime
from src.models import db, User, MessageLog
from src.services.ai_service import AIService

class SMSService:
    def __init__(self):
        self.sms = africastalking.SMS
        self.ai_service = AIService()
        self.shortcode = '15629'  # Your Africa's Talking shortcode
    
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
