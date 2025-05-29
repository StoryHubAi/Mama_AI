import os
import africastalking
from datetime import datetime
from src.models import db, User, Pregnancy, MessageLog
from src.utils.language_utils import get_translation
from src.services.ai_service import AIService

class USSDService:
    def __init__(self):
        self.ai_service = AIService()
        
    def handle_request(self, session_id, phone_number, text, service_code):
        """Handle USSD request and return appropriate response"""
        
        # Log the USSD request
        self._log_message(phone_number, "USSD", "incoming", text, session_id)
        
        # Clean phone number
        clean_phone = self._clean_phone_number(phone_number)
        
        # Get or create user
        user = self._get_or_create_user(clean_phone)
        
        # Parse USSD input
        inputs = text.split('*') if text else []
        
        if text == '':
            # Main menu
            response = self._main_menu(user)
        elif len(inputs) == 1:
            # First level menu
            response = self._handle_first_level(inputs[0], user, session_id)
        else:
            # Deeper menu levels
            response = self._handle_deep_menu(inputs, user, session_id)
          # Log the response
        self._log_message(clean_phone, "USSD", "outgoing", response, session_id)
        
        return response
    
    def _main_menu(self, user):
        """Return the main USSD menu"""
        lang = user.preferred_language
        
        menu = get_translation(lang, "main_menu", 
            "Welcome to MAMA-AI 🤱\n"
            "1. Pregnancy Tracking\n"
            "2. Health Check\n"
            "3. Appointments\n"
            "4. Emergency\n"
            "5. Settings\n"
            "6. Get Help\n"
            "7. 🎙️ Voice Assistant"
        )
        
        return f"CON {menu}"
    
    def _handle_first_level(self, choice, user, session_id):
        """Handle first level menu choices"""
        lang = user.preferred_language
        
        if choice == '1':
            # Pregnancy Tracking
            pregnancy = self._get_active_pregnancy(user)
            if pregnancy:
                weeks = pregnancy.weeks_pregnant or 0
                menu = get_translation(lang, "pregnancy_menu",
                    f"Pregnancy Tracking (Week {weeks})\n"
                    "1. Update symptoms\n"
                    "2. Track baby's movement\n"
                    "3. Nutrition tips\n"
                    "4. Weekly info\n"
                    "0. Back"
                )
            else:
                menu = get_translation(lang, "no_pregnancy",
                    "No active pregnancy found.\n"
                    "1. Register new pregnancy\n"
                    "0. Back to main menu"
                )
            return f"CON {menu}"
            
        elif choice == '2':
            # Health Check
            menu = get_translation(lang, "health_menu",
                "Health Check 🏥\n"
                "1. Report symptoms\n"
                "2. Ask health question\n"
                "3. Emergency symptoms\n"
                "4. Medication reminder\n"
                "0. Back"
            )
            return f"CON {menu}"
            
        elif choice == '3':
            # Appointments
            menu = get_translation(lang, "appointments_menu",
                "Appointments 📅\n"
                "1. View next appointment\n"
                "2. Schedule appointment\n"
                "3. Appointment history\n"
                "0. Back"
            )
            return f"CON {menu}"
            
        elif choice == '4':
            # Emergency
            return self._handle_emergency(user)
            
        elif choice == '5':
            # Settings
            menu = get_translation(lang, "settings_menu",
                "Settings ⚙️\n"
                "1. Change language\n"
                "2. Update profile\n"            "3. Emergency contacts\n"
                "0. Back"
            )
            return f"CON {menu}"
        
        elif choice == '6':
            # Help
            help_text = get_translation(lang, "help_text",
                "MAMA-AI Help 📖\n"
                "This service provides:\n"
                "• Pregnancy tracking\n"
                "• Health advice\n"
                "• Emergency support\n"
                "• Appointment reminders\n\n"
                "For emergencies, dial 911\n"
                "SMS 'HELP' for more info"
            )
            return f"END {help_text}"
        
        elif choice == '7':
            # Voice Assistant
            voice_number = os.getenv('VOICE_PHONE_NUMBER', '+254727230675')
            voice_text = get_translation(lang, "voice_assistant",
                f"🎙️ Voice Assistant\n"
                f"Call {voice_number} to access:\n"
                "• Voice-guided menus\n"
                "• Speak your questions\n"
                "• AI voice responses\n"
                "• Hands-free assistance\n\n"
                "The call is FREE!\n"
                "Dial now for voice help."
            )
            return f"END {voice_text}"
        
        else:
            error_msg = get_translation(lang, "invalid_choice", "Invalid choice. Please try again.")
            return f"END {error_msg}"
    
    def _handle_deep_menu(self, inputs, user, session_id):
        """Handle deeper menu navigation"""
        lang = user.preferred_language
        
        if inputs[0] == '1':  # Pregnancy tracking submenu
            if len(inputs) == 2:
                if inputs[1] == '1':
                    # Update symptoms
                    return f"CON {get_translation(lang, 'enter_symptoms', 'Please describe your current symptoms:')}"
                elif inputs[1] == '2':
                    # Track baby's movement
                    return f"CON {get_translation(lang, 'baby_movement', 'How many times did you feel baby move in the last hour?\\n1. Less than 3\\n2. 3-5 times\\n3. More than 5')}"
                elif inputs[1] == '3':
                    # Nutrition tips
                    tips = self.ai_service.get_nutrition_tips(user)
                    return f"END {tips}"
                elif inputs[1] == '4':
                    # Weekly info
                    pregnancy = self._get_active_pregnancy(user)
                    if pregnancy:
                        info = self.ai_service.get_weekly_info(pregnancy.weeks_pregnant)
                        return f"END {info}"
            elif len(inputs) == 3:
                if inputs[1] == '1':
                    # Process symptoms
                    symptoms = inputs[2]
                    response = self.ai_service.analyze_symptoms(symptoms, user)
                    self._update_pregnancy_symptoms(user, symptoms)
                    return f"END {response}"
                elif inputs[1] == '2':
                    # Process baby movement
                    movement = inputs[2]
                    response = self.ai_service.analyze_baby_movement(movement, user)
                    return f"END {response}"
        
        elif inputs[0] == '2':  # Health check submenu
            if len(inputs) == 2:
                if inputs[1] == '1':
                    return f"CON {get_translation(lang, 'report_symptoms', 'Describe your symptoms in detail:')}"
                elif inputs[1] == '2':
                    return f"CON {get_translation(lang, 'ask_question', 'What health question do you have?')}"
            elif len(inputs) == 3:
                if inputs[1] == '1':
                    # Process reported symptoms
                    symptoms = inputs[2]
                    response = self.ai_service.analyze_symptoms(symptoms, user)
                    return f"END {response}"
                elif inputs[1] == '2':
                    # Answer health question
                    question = inputs[2]
                    answer = self.ai_service.answer_health_question(question, user)
                    return f"END {answer}"
        
        elif inputs[0] == '5':  # Settings submenu
            if len(inputs) == 2:
                if inputs[1] == '1':
                    return f"CON {get_translation(lang, 'choose_language', 'Choose language:\\n1. English\\n2. Kiswahili')}"
                elif inputs[1] == '2':
                    return f"CON {get_translation(lang, 'update_profile', 'Enter your name:')}"
            elif len(inputs) == 3:
                if inputs[1] == '1':
                    # Change language
                    new_lang = 'en' if inputs[2] == '1' else 'sw'
                    self._update_user_language(user, new_lang)
                    return f"END {get_translation(new_lang, 'language_changed', 'Language updated successfully!')}"
                elif inputs[1] == '2':
                    # Update name
                    name = inputs[2]
                    self._update_user_name(user, name)
                    return f"END {get_translation(lang, 'name_updated', f'Name updated to {name}')}"
        
        # Default response for unhandled deep menu
        return f"END {get_translation(lang, 'invalid_option', 'Invalid option selected.')}"
    
    def _handle_emergency(self, user):
        """Handle emergency situations"""
        lang = user.preferred_language
        
        # This is an emergency - provide immediate guidance
        emergency_msg = get_translation(lang, "emergency_response",
            "🚨 EMERGENCY DETECTED 🚨\n\n"
            "If life-threatening:\n"
            "CALL 911 IMMEDIATELY\n\n"
            "Common pregnancy emergencies:\n"
            "• Severe bleeding\n"
            "• Severe abdominal pain\n"
            "• Vision problems\n"
            "• Severe headaches\n\n"
            "We're sending your emergency contact a message.\n\n"
            "Stay calm and seek immediate medical help."
        )
        
        # Trigger emergency alert
        self._trigger_emergency_alert(user)
        
        return f"END {emergency_msg}"
    
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
    
    def _get_active_pregnancy(self, user):
        """Get user's active pregnancy"""
        return Pregnancy.query.filter_by(
            user_id=user.id, 
            is_active=True
        ).first()
    
    def _update_pregnancy_symptoms(self, user, symptoms):
        """Update pregnancy symptoms"""
        pregnancy = self._get_active_pregnancy(user)
        if pregnancy:
            pregnancy.current_symptoms = symptoms
            pregnancy.updated_at = datetime.utcnow()
            db.session.commit()
    
    def _update_user_language(self, user, language):
        """Update user's preferred language"""
        user.preferred_language = language
        user.updated_at = datetime.utcnow()
        db.session.commit()
    
    def _update_user_name(self, user, name):
        """Update user's name"""
        user.name = name
        user.updated_at = datetime.utcnow()
        db.session.commit()
    
    def _trigger_emergency_alert(self, user):
        """Trigger emergency alert and notifications"""
        # This would trigger SMS to emergency contacts
        # and create an emergency alert record
        from src.services.sms_service import SMSService
        sms_service = SMSService()
        
        if user.emergency_contact:
            emergency_msg = f"EMERGENCY: {user.name or user.phone_number} has triggered an emergency alert through MAMA-AI. Please check on them immediately."
            sms_service.send_sms(user.emergency_contact, emergency_msg)
    
    def _clean_phone_number(self, phone_number):
        """Clean and standardize phone number"""
        # Remove any non-digit characters except +
        clean = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Add country code if not present (assuming Kenya +254)
        if not clean.startswith('+'):
            if clean.startswith('0'):
                clean = '+254' + clean[1:]
            elif clean.startswith('254'):
                clean = '+' + clean
            else:
                clean = '+254' + clean
        
        return clean
    
    def _log_message(self, phone_number, msg_type, direction, content, session_id=None):
        """Log USSD message"""
        log = MessageLog(
            phone_number=phone_number,
            message_type=msg_type,
            direction=direction,
            content=content,
            session_id=session_id
        )
        db.session.add(log)
        db.session.commit()
