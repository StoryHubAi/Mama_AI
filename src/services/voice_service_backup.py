import os
import africastalking
from datetime import datetime
from src.models import db, User, MessageLog
from src.utils.language_utils import get_translation
from src.services.ai_service import AIService

class VoiceService:
    """
    Voice Service for handling Africa's Talking Voice API integration
    This service manages incoming and outgoing voice calls for MAMA-AI
    """
    
    def __init__(self):
        """Initialize the Voice Service"""
        self.voice = africastalking.Voice
        self.ai_service = AIService()
        
    def handle_incoming_call(self, session_id, phone_number, is_active=None):
        """
        Handle incoming voice calls from Africa's Talking
        
        Args:
            session_id: Unique session identifier for the call
            phone_number: Caller's phone number
            is_active: Whether the call is active (1) or ended (0)
            
        Returns:
            XML response for Africa's Talking Voice API
        """
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
        """
        Handle DTMF (keypad) input during voice calls
        
        Args:
            session_id: Call session ID
            phone_number: Caller's phone number  
            dtmf_digits: The digits pressed by user
            
        Returns:
            XML response with next action
        """
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
        """
        Make an outbound call with a voice message
        
        Args:
            phone_number: Number to call
            message: Message to speak
            voice_type: Voice type ("man" or "woman")
            
        Returns:
            Call response from Africa's Talking
        """
        try:
            clean_phone = self._clean_phone_number(phone_number)
            
            # Create XML for outbound call
            call_xml = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="{voice_type}">{message}</Say>
                <Hangup/>
            </Response>
            """
            
            # Make the call
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
        menu_1 = get_translation("Press 1 for pregnancy tracking", language)
        menu_2 = get_translation("Press 2 for health check", language)
        menu_3 = get_translation("Press 3 for appointments", language)
        menu_4 = get_translation("Press 4 for emergency", language)
        menu_9 = get_translation("Press 9 to repeat menu", language)
        
        xml_response = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">{welcome_message}</Say>
            <Say voice="woman">{menu_1}</Say>
            <Say voice="woman">{menu_2}</Say>
            <Say voice="woman">{menu_3}</Say>
            <Say voice="woman">{menu_4}</Say>
            <Say voice="woman">{menu_9}</Say>
            <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice/dtmf"/>
        </Response>
        """
        
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
            invalid_msg = get_translation("Invalid option. Please try again.", language)
            welcome_message = self._get_welcome_message(user)
            
            xml_response = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="woman">{invalid_msg}</Say>
                {self._create_voice_menu_response(welcome_message, user)}
            </Response>
            """
            return xml_response
    
    def _handle_pregnancy_tracking(self, user, session_id):
        """Handle pregnancy tracking voice interaction"""
        language = user.preferred_language or 'en'
        
        # Get pregnancy information
        pregnancy = self.ai_service._get_active_pregnancy(user)
        
        if pregnancy:
            weeks = pregnancy.weeks_pregnant
            message = get_translation(
                f"You are {weeks} weeks pregnant. How are you feeling today? Press 1 for good, 2 for some concerns, 3 for urgent help.",
                language
            )
        else:
            message = get_translation(
                "Let me help you start tracking your pregnancy. Press 1 to register new pregnancy, 0 to return to main menu.",
                language
            )
        
        xml_response = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">{message}</Say>
            <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice/pregnancy"/>
        </Response>
        """
        
        return xml_response
    
    def _handle_health_check(self, user, session_id):
        """Handle health check voice interaction"""
        language = user.preferred_language or 'en'
        
        message = get_translation(
            "Health check menu. Press 1 to report symptoms, 2 for general health advice, 3 for nutrition tips, 0 for main menu.",
            language
        )
        
        xml_response = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">{message}</Say>
            <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice/health"/>
        </Response>
        """
        
        return xml_response
    
    def _handle_appointments(self, user, session_id):
        """Handle appointments voice interaction"""
        language = user.preferred_language or 'en'
        
        # Get upcoming appointments
        upcoming_appointments = user.appointments.filter_by(status='scheduled').all()
        
        if upcoming_appointments:
            next_appointment = upcoming_appointments[0]
            message = get_translation(
                f"Your next appointment is on {next_appointment.appointment_date.strftime('%B %d')}. Press 1 for reminder, 2 to reschedule, 0 for main menu.",
                language
            )
        else:
            message = get_translation(
                "You have no scheduled appointments. Press 1 to schedule new appointment, 0 for main menu.",
                language
            )
        
        xml_response = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">{message}</Say>
            <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice/appointments"/>
        </Response>
        """
        
        return xml_response
    
    def _handle_emergency(self, user, session_id):
        """Handle emergency voice interaction with immediate response"""
        language = user.preferred_language or 'en'
        
        emergency_msg = get_translation(
            "This is an emergency. Stay calm. Press 1 if you're experiencing severe bleeding, 2 for severe pain, 3 for other emergency, 9 to speak with emergency services immediately.",
            language
        )
        
        # Log emergency call
        self._log_call(session_id, user.phone_number, "emergency", "emergency_menu_accessed")
        
        xml_response = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">{emergency_msg}</Say>
            <GetDigits timeout="15" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice/emergency"/>
        </Response>
        """
        
        return xml_response
    
    def _get_welcome_message(self, user):
        """Get personalized welcome message"""
        language = user.preferred_language or 'en'
        
        if user.name:
            welcome = get_translation(f"Hello {user.name}, welcome to MAMA-AI, your maternal health assistant.", language)
        else:
            welcome = get_translation("Welcome to MAMA-AI, your maternal health assistant.", language)
        
        return welcome
    
    def _create_error_response(self):
        """Create error response XML"""
        return """
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">Sorry, there was an error. Please try again later.</Say>
            <Hangup/>
        </Response>
        """
    
    def _get_callback_url(self):
        """Get the base callback URL for voice webhooks"""
        # In production, this should be your deployed domain
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
            else:                phone = '+254' + phone
                
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
    
    def _process_pregnancy_input(self, dtmf_digits, user, session_id):
        """Process pregnancy-specific DTMF input"""
        language = user.preferred_language or 'en'
        
        if dtmf_digits == "1":
            # Good feeling
            message = get_translation("Great to hear you're feeling good! Remember to take your vitamins and stay hydrated. Press 0 for main menu.", language)
        elif dtmf_digits == "2":
            # Some concerns
            message = get_translation("I understand you have some concerns. Press 1 for nausea help, 2 for back pain advice, 3 to speak with a nurse, 0 for main menu.", language)
        elif dtmf_digits == "3":
            # Urgent help
            return self._handle_emergency(user, session_id)
        elif dtmf_digits == "0":
            # Return to main menu
            welcome_message = self._get_welcome_message(user)
            return self._create_voice_menu_response(welcome_message, user)
        else:
            message = get_translation("Invalid option. Press 1 for good, 2 for concerns, 3 for urgent help, 0 for main menu.", language)
        
        xml_response = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">{message}</Say>
            <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice/pregnancy"/>
        </Response>
        """
        
        return xml_response
    
    def _process_health_input(self, dtmf_digits, user, session_id):
        """Process health check DTMF input"""
        language = user.preferred_language or 'en'
        
        if dtmf_digits == "1":
            # Report symptoms
            message = get_translation("To report symptoms, press 1 for fever, 2 for headache, 3 for severe pain, 4 for bleeding, 0 for main menu.", language)
        elif dtmf_digits == "2":
            # General health advice
            message = get_translation("For healthy pregnancy: eat nutritious foods, exercise gently, get enough rest, attend all checkups. Press 0 for main menu.", language)
        elif dtmf_digits == "3":
            # Nutrition tips
            message = get_translation("Eat plenty of fruits, vegetables, whole grains, and lean proteins. Take folic acid supplements. Avoid alcohol and raw foods. Press 0 for main menu.", language)
        elif dtmf_digits == "0":
            # Return to main menu
            welcome_message = self._get_welcome_message(user)
            return self._create_voice_menu_response(welcome_message, user)
        else:
            message = get_translation("Invalid option. Press 1 for symptoms, 2 for general advice, 3 for nutrition, 0 for main menu.", language)
        
        xml_response = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">{message}</Say>
            <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice/health"/>
        </Response>
        """
        
        return xml_response
    
    def _process_appointments_input(self, dtmf_digits, user, session_id):
        """Process appointments DTMF input"""
        language = user.preferred_language or 'en'
        
        if dtmf_digits == "1":
            # Schedule new appointment or set reminder
            upcoming_appointments = user.appointments.filter_by(status='scheduled').all()
            if upcoming_appointments:
                message = get_translation("Reminder set for your upcoming appointment. You'll receive an SMS. Press 0 for main menu.", language)
            else:
                message = get_translation("To schedule an appointment, please visit your nearest health clinic or call them directly. Press 0 for main menu.", language)
        elif dtmf_digits == "2":
            # Reschedule
            message = get_translation("To reschedule your appointment, please contact your health clinic directly. Press 0 for main menu.", language)
        elif dtmf_digits == "0":
            # Return to main menu
            welcome_message = self._get_welcome_message(user)
            return self._create_voice_menu_response(welcome_message, user)
        else:
            message = get_translation("Invalid option. Press 1 for reminder, 2 to reschedule, 0 for main menu.", language)
        
        xml_response = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">{message}</Say>
            <GetDigits timeout="30" finishOnKey="#" numDigits="1" callbackUrl="{self._get_callback_url()}/voice/appointments"/>
        </Response>
        """
        
        return xml_response
    
    def _process_emergency_input(self, dtmf_digits, user, session_id):
        """Process emergency DTMF input with immediate response"""
        language = user.preferred_language or 'en'
        
        # Log emergency interaction
        self._log_call(session_id, user.phone_number, "emergency", f"Emergency option: {dtmf_digits}")
        
        if dtmf_digits == "1":
            # Severe bleeding
            message = get_translation("Severe bleeding is serious. Go to the nearest hospital immediately. Call emergency services now. Do not wait. Stay calm and get help.", language)
            
            # Also trigger emergency SMS
            try:
                from src.services.sms_service import SMSService
                sms_service = SMSService()
                emergency_sms = get_translation("EMERGENCY: Severe bleeding reported. Seeking immediate medical attention. Location needed.", language)
                sms_service.send_sms(user.phone_number, emergency_sms)
            except:
                pass
                
        elif dtmf_digits == "2":
            # Severe pain
            message = get_translation("Severe pain during pregnancy needs immediate attention. Go to hospital now. Call emergency services if pain is extreme.", language)
            
        elif dtmf_digits == "3":
            # Other emergency
            message = get_translation("For any pregnancy emergency, contact your doctor immediately or go to the nearest hospital. Do not delay seeking help.", language)
            
        elif dtmf_digits == "9":
            # Connect to emergency services
            message = get_translation("Connecting you to emergency services. Please hold. If this fails, dial your local emergency number immediately.", language)
            # In a real implementation, this would forward to emergency services
            
        else:
            message = get_translation("Emergency: Press 1 for bleeding, 2 for severe pain, 3 for other emergency, 9 for emergency services.", language)
        
        xml_response = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="woman">{message}</Say>
            <Hangup/>
        </Response>
        """
        
        return xml_response
