import os
import africastalking
from datetime import datetime
from src.models import db, User, MessageLog
from src.utils.language_utils import get_translation
from src.services.ai_service import AIService

class VoiceService:
    """Voice Service for handling Africa's Talking Voice API integration"""
    
    def __init__(self):
        """Initialize the Voice Service"""
        self.voice = africastalking.Voice
        self.ai_service = AIService()
        
    def handle_incoming_call(self, session_id, phone_number, is_active=None):
        """Handle incoming voice calls from Africa's Talking"""
        try:
            # Clean and get user
            clean_phone = self._clean_phone_number(phone_number)
            user = self._get_or_create_user(clean_phone)
            
            # Log the incoming call
            self._log_call(session_id, clean_phone, "incoming", "call_started")
            
            # Generate welcome message based on user's language
            welcome_message = self._get_welcome_message(user)
            
            # Create voice response with menu options
            response = self._create_voice_menu_response(welcome_message, user)
            
            return response
            
        except Exception as e:
            print(f"Error handling incoming call: {str(e)}")
            return self._create_error_response()
    
    def handle_dtmf_input(self, session_id, phone_number, dtmf_digits):
        """Handle DTMF (keypad) input during voice calls"""
        try:
            clean_phone = self._clean_phone_number(phone_number)
            user = self._get_or_create_user(clean_phone)
            
            # Log the DTMF input
            self._log_call(session_id, clean_phone, "dtmf", dtmf_digits)
            
            # Process the menu selection
            response = self._process_menu_selection(dtmf_digits, user, session_id)
            
            return response
            
        except Exception as e:
            print(f"Error handling DTMF input: {str(e)}")
            return self._create_error_response()
    
    def make_outbound_call(self, phone_number, message, voice_type="woman"):
        """Make an outbound call with a voice message"""
        try:
            clean_phone = self._clean_phone_number(phone_number)
            
            # Make the call using Africa's Talking
            response = self.voice.call(
                source=os.getenv('AFRICASTALKING_SHORTCODE'),
                destination=clean_phone
            )
            
            # Log the outbound call
            self._log_call("outbound", clean_phone, "outgoing", message)
            
            return response
            
        except Exception as e:
            print(f"Error making outbound call: {str(e)}")
            return None
    
    def _get_translation(self, text, language='en'):
        """Helper function to get translation with proper parameter order"""
        try:
            return get_translation(language, text, text)
        except:
            return text  # Fallback to original text if translation fails
    
    def _create_voice_menu_response(self, welcome_message, user):
        """Create the main voice menu XML response"""
        language = user.preferred_language or 'en'
        
        # Get menu options in user's language
        menu_1 = self._get_translation("Press 1 for pregnancy tracking", language)
        menu_2 = self._get_translation("Press 2 for health check", language)
        menu_3 = self._get_translation("Press 3 for appointments", language)
        menu_4 = self._get_translation("Press 4 for emergency", language)
        menu_9 = self._get_translation("Press 9 to repeat menu", language)
        
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman">{welcome_message}</Say>
    <Say voice="woman">{menu_1}</Say>
    <Say voice="woman">{menu_2}</Say>
    <Say voice="woman">{menu_3}</Say>
    <Say voice="woman">{menu_4}</Say>
    <Say voice="woman">{menu_9}</Say>
    <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice"/>
</Response>"""
        
        return xml_response
    
    def _process_menu_selection(self, dtmf_digits, user, session_id):
        """Process user's menu selection"""
        language = user.preferred_language or 'en'
        
        if dtmf_digits == "1":
            # Pregnancy tracking
            return self._handle_pregnancy_tracking(user, session_id)
        elif dtmf_digits == "2":
            # Health check
            return self._handle_health_check(user, session_id)
        elif dtmf_digits == "3":
            # Appointments
            return self._handle_appointments(user, session_id)
        elif dtmf_digits == "4":
            # Emergency
            return self._handle_emergency(user, session_id)
        elif dtmf_digits == "9":
            # Repeat menu
            welcome_message = self._get_welcome_message(user)
            return self._create_voice_menu_response(welcome_message, user)
        else:
            # Invalid option
            invalid_msg = self._get_translation("Invalid option. Please try again.", language)
            welcome_message = self._get_welcome_message(user)
            
            xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman">{invalid_msg}</Say>
    <Say voice="woman">{welcome_message}</Say>
    <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice"/>
</Response>"""
            return xml_response
    
    def _handle_pregnancy_tracking(self, user, session_id):
        """Handle pregnancy tracking voice interaction"""
        language = user.preferred_language or 'en'
        
        message = self._get_translation(
            "Pregnancy tracking. Press 1 if feeling good, 2 for some concerns, 3 for urgent help, 0 for main menu.",
            language
        )
        
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman">{message}</Say>
    <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice"/>
</Response>"""
        
        return xml_response
    
    def _handle_health_check(self, user, session_id):
        """Handle health check voice interaction"""
        language = user.preferred_language or 'en'
        
        message = self._get_translation(
            "Health check menu. Press 1 to report symptoms, 2 for general health advice, 3 for nutrition tips, 0 for main menu.",
            language
        )
        
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman">{message}</Say>
    <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice"/>
</Response>"""
        
        return xml_response
    
    def _handle_appointments(self, user, session_id):
        """Handle appointments voice interaction"""
        language = user.preferred_language or 'en'
        
        message = self._get_translation(
            "Appointments menu. Press 1 for next appointment, 2 to schedule appointment, 0 for main menu.",
            language
        )
        
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman">{message}</Say>
    <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice"/>
</Response>"""
        
        return xml_response
    
    def _handle_emergency(self, user, session_id):
        """Handle emergency voice interaction with immediate response"""
        language = user.preferred_language or 'en'
        
        emergency_msg = self._get_translation(
            "Emergency assistance. Stay calm. Press 1 for severe bleeding, 2 for severe pain, 3 for other emergency.",
            language
        )
        
        # Log emergency call
        self._log_call(session_id, user.phone_number, "emergency", "emergency_menu_accessed")
        
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman">{emergency_msg}</Say>
    <Say voice="woman">If this is life threatening, hang up and call emergency services immediately.</Say>
    <GetDigits timeout="15" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice"/>
</Response>"""
        
        return xml_response
    
    def _get_welcome_message(self, user):
        """Get personalized welcome message"""
        language = user.preferred_language or 'en'
        
        if user.name:
            welcome = self._get_translation(f"Hello {user.name}, welcome to MAMA-AI, your maternal health assistant.", language)
        else:
            welcome = self._get_translation("Welcome to MAMA-AI, your maternal health assistant.", language)
        
        return welcome
    
    def _create_error_response(self):
        """Create error response XML"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="woman">Sorry, there was an error. Please try again later.</Say>
    <Hangup/>
</Response>"""
    
    def _get_callback_url(self):
        """Get the base callback URL for voice webhooks"""
        base_url = os.getenv('BASE_URL', 'https://your-domain.com')
        return base_url
    
    def _clean_phone_number(self, phone_number):
        """Clean and format phone number"""
        if not phone_number:
            return None
            
        # Remove any non-digit characters except +
        phone = ''.join(char for char in phone_number if char.isdigit() or char == '+')
        
        # Ensure it starts with + for international format
        if not phone.startswith('+'):
            # Assume it's a Kenyan number if no country code
            if phone.startswith('0'):
                phone = '+254' + phone[1:]
            elif phone.startswith('254'):
                phone = '+' + phone
            else:
                phone = '+254' + phone
                
        return phone
    
    def _get_or_create_user(self, phone_number):
        """Get existing user or create new one"""
        user = User.query.filter_by(phone_number=phone_number).first()
        
        if not user:
            user = User(
                phone_number=phone_number,
                preferred_language='en',
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            
        return user
    
    def _log_call(self, session_id, phone_number, call_type, content):
        """Log voice call interactions"""
        try:
            log_entry = MessageLog(
                phone_number=phone_number,
                message_type="VOICE",
                direction=call_type,
                content=content,
                session_id=session_id
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            print(f"Error logging call: {str(e)}")
