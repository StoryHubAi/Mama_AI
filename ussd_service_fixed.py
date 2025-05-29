import os
import africastalking
from datetime import datetime
from src.models import db, User, Pregnancy, MessageLog, Appointment
from src.utils.language_utils import get_translation
from src.services.ai_service import AIService

class USSDService:
    def __init__(self):
        self.ai_service = AIService()
        
    def handle_request(self, session_id, phone_number, text, service_code):
        """Handle USSD request following simplified user journey"""
        
        # Log the USSD request
        self._log_message(phone_number, "USSD", "incoming", text, session_id)
        
        # Clean phone number
        clean_phone = self._clean_phone_number(phone_number)
        
        # Get or create user
        user = self._get_or_create_user(clean_phone)
        
        # Parse USSD input
        inputs = text.split('*') if text else []
        
        try:
            if text == '':
                # Check if new user needs registration
                if not user.name or not user.preferred_language:
                    response = self._start_registration(user)
                else:
                    response = self._main_menu(user)
            else:
                # Handle all menu navigation
                response = self._handle_navigation(inputs, user, session_id)
        except Exception as e:
            print(f"❌ USSD Error: {str(e)}")
            response = self._get_error_response(user)
        
        # Log the response
        self._log_message(clean_phone, "USSD", "outgoing", response, session_id)
        
        return response
      
    def _start_registration(self, user):
        """Start new user registration - Step 1: Language Selection"""
        return (
            "CON Welcome to MAMA-AI 🤱\n"
            "Karibu MAMA-AI 🤱\n\n"
            "Choose your language:\n"
            "Chagua lugha yako:\n\n"
            "1. English\n"
            "2. Kiswahili"
        )
    
    def _main_menu(self, user):
        """Return simplified main menu for registered users"""
        lang = user.preferred_language
        
        if lang == 'sw':
            menu = (
                f"Karibu {user.name or 'Mama'} 🤱\n\n"
                "1. Uliza swali la afya\n"
                "2. Angalia dalili\n" 
                "3. Msaada wa haraka\n"
                "0. Ondoka"
            )
        else:
            menu = (
                f"Welcome {user.name or 'Mama'} 🤱\n\n"
                "1. Ask health question\n"
                "2. Check symptoms\n"
                "3. Emergency help\n"
                "0. Exit"
            )
        
        return f"CON {menu}"
    
    def _handle_navigation(self, inputs, user, session_id):
        """Handle all USSD navigation based on user journey"""
        
        # New user registration flow
        if not user.name or not user.preferred_language:
            return self._handle_registration_flow(inputs, user)
        
        # Registered user main menu navigation
        if len(inputs) == 1:
            return self._handle_main_menu_selection(inputs[0], user, session_id)
        
        # Multi-step interactions (symptoms, questions)
        return self._handle_multi_step_interaction(inputs, user, session_id)
    
    def _handle_registration_flow(self, inputs, user):
        """Handle new user registration steps"""
        
        if len(inputs) == 1:
            # Step 1: Language selection
            if inputs[0] == '1':
                # English selected
                user.preferred_language = 'en'
                db.session.commit()
                return (
                    "CON Great! Now please enter your name:\n"
                    "(This helps us personalize your experience)"
                )
            elif inputs[0] == '2':
                # Kiswahili selected
                user.preferred_language = 'sw' 
                db.session.commit()
                return (
                    "CON Vizuri! Sasa tafadhali andika jina lako:\n"
                    "(Hii inatusaidia kukupa huduma maalum)"
                )
            else:
                return "END Invalid choice. Please dial again."
        
        elif len(inputs) == 2:
            # Step 2: Name entry
            name = inputs[1].strip()
            if len(name) < 2:
                lang = user.preferred_language
                if lang == 'sw':
                    return "CON Jina fupi sana. Tafadhali andika jina kamili:"
                else:
                    return "CON Name too short. Please enter your full name:"
            
            user.name = name
            db.session.commit()
            
            lang = user.preferred_language
            if lang == 'sw':
                return (
                    f"CON Asante {name}! 🤱\n\n"
                    "Je, una mimba sasa hivi?\n\n"
                    "1. Ndio\n"
                    "2. Hapana\n"
                    "3. Sijui"
                )
            else:
                return (
                    f"CON Thank you {name}! 🤱\n\n"
                    "Are you currently pregnant?\n\n"
                    "1. Yes\n"
                    "2. No\n"
                    "3. Not sure"
                )
        
        elif len(inputs) == 3:
            # Step 3: Pregnancy status
            pregnancy_status = inputs[2]
            lang = user.preferred_language
            
            if pregnancy_status == '1':  # Yes, pregnant
                if lang == 'sw':
                    return (
                        "CON Wiki ngapi za ujauzito?\n"
                        "(Andika namba ya wiki, mfano: 12)\n\n"
                        "Kama hujui, andika 0"
                    )
                else:
                    return (
                        "CON How many weeks pregnant?\n"
                        "(Enter number of weeks, e.g: 12)\n\n"
                        "If unsure, enter 0"
                    )
            elif pregnancy_status == '2':  # No, not pregnant
                if lang == 'sw':
                    return (
                        f"END Karibu MAMA-AI, {user.name}! 🤱\n\n"
                        "Umesajiliwa kikamilifu.\n"
                        "Piga *15629# wakati wowote kupata msaada wa afya ya mama na mtoto."
                    )
                else:
                    return (
                        f"END Welcome to MAMA-AI, {user.name}! 🤱\n\n"
                        "Registration complete.\n"
                        "Dial *15629# anytime for maternal and child health support."
                    )
            elif pregnancy_status == '3':  # Not sure
                if lang == 'sw':
                    return (
                        "END Enda kwa daktari kujua kama una mimba.\n\n"
                        f"Karibu tena, {user.name}! 🤱\n"
                        "Piga *15629# baadaye."
                    )
                else:
                    return (
                        "END Please visit a healthcare provider to confirm pregnancy.\n\n"
                        f"Welcome {user.name}! 🤱\n"
                        "Dial *15629# anytime for support."
                    )
        
        elif len(inputs) == 4:
            # Step 4: Pregnancy weeks
            try:
                weeks = int(inputs[3])
                if weeks < 0 or weeks > 42:
                    lang = user.preferred_language
                    if lang == 'sw':
                        return "CON Namba si sahihi. Andika wiki 0-42:"
                    else:
                        return "CON Invalid number. Enter weeks 0-42:"
                
                # Create pregnancy record
                pregnancy = Pregnancy(
                    user_id=user.id,
                    weeks_pregnant=weeks if weeks > 0 else None,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(pregnancy)
                db.session.commit()
                
                lang = user.preferred_language
                week_text = f" ya wiki {weeks}" if weeks > 0 else ""
                week_text_en = f" at {weeks} weeks" if weeks > 0 else ""
                
                if lang == 'sw':
                    return (
                        f"END Hongera {user.name}! 🤱\n\n"
                        f"Umesajiliwa kama mama mja wazito{week_text}.\n\n"
                        "Piga *15629# wakati wowote:\n"
                        "• Kuuliza maswali ya afya\n"
                        "• Kuangalia dalili\n" 
                        "• Kupata msaada wa haraka"
                    )
                else:
                    return (
                        f"END Congratulations {user.name}! 🤱\n\n"
                        f"You're registered as an expectant mother{week_text_en}.\n\n"
                        "Dial *15629# anytime to:\n"
                        "• Ask health questions\n"
                        "• Check symptoms\n"
                        "• Get emergency help"
                    )
            except ValueError:
                lang = user.preferred_language
                if lang == 'sw':
                    return "CON Andika namba tu (mfano: 12):"
                else:
                    return "CON Enter numbers only (e.g: 12):"
        
        # Fallback
        return "END Registration incomplete. Please dial *15629# to start again."
    
    def _handle_main_menu_selection(self, choice, user, session_id):
        """Handle main menu selections for registered users"""
        lang = user.preferred_language
        
        if choice == '1':
            # Start AI chat conversation - Direct prompt
            if lang == 'sw':
                return "CON 🤖 Mazungumzo na MAMA-AI\n\nAndika swali lako la afya:"
            else:
                return "CON 🤖 Chat with MAMA-AI\n\nEnter your health question:"
                
        elif choice == '2':
            # Start symptom checker - Direct prompt  
            if lang == 'sw':
                return "CON 🩺 Angalia Dalili na AI\n\nEleza dalili zako:"
            else:
                return "CON 🩺 Symptom Check with AI\n\nDescribe your symptoms:"
                
        elif choice == '3':
            # Emergency help
            return self._handle_emergency(user)
            
        elif choice == '0':
            # Exit
            if lang == 'sw':
                return f"END Asante {user.name}! Piga *15629# wakati wowote. 🤱"
            else:
                return f"END Thank you {user.name}! Dial *15629# anytime. 🤱"
        else:
            if lang == 'sw':
                return "END Chaguo batili. Piga *15629# tena."
            else:
                return "END Invalid choice. Dial *15629# again."
    
    def _handle_multi_step_interaction(self, inputs, user, session_id):
        """Handle conversational AI chat with visible conversation history"""
        lang = user.preferred_language
        
        try:
            # Check if AI is available first
            if not self.ai_service.client:
                if lang == 'sw':
                    return "END AI haipo sasa. Jaribu tena baadaye."
                else:
                    return "END AI not available. Please try again later."
            
            # Extract conversation context
            chat_type = inputs[0]  # '1' for health chat, '2' for symptoms
            user_message = ' '.join(inputs[1:])
            
            # Handle exit command
            if user_message.strip() == '0':
                if lang == 'sw':
                    return f"END Asante {user.name}! Piga *15629# wakati wowote. 🤱"
                else:
                    return f"END Thank you {user.name}! Dial *15629# anytime. 🤱"
            
            # Get pregnancy context for AI
            pregnancy = self._get_active_pregnancy(user)
            context_info = ""
            if pregnancy and pregnancy.weeks_pregnant:
                context_info = f" [User is {pregnancy.weeks_pregnant} weeks pregnant]"
            
            # Create session-specific key for conversation history
            session_key = f"ussd_{session_id}_{chat_type}"
            
            # Prepare AI message with context
            ai_prompt = f"{user_message}{context_info}"
            
            # Get AI response - PURE AI, no hardcoding
            ai_response = self.ai_service.chat_with_ai(
                user_message=ai_prompt,
                user=user,
                session_id=session_key,
                channel='USSD'
            )
            
            # Build conversation display with current exchange
            conversation_display = self._build_conversation_display(
                user_message, ai_response, lang
            )
            
            # Add conversation continuation prompt
            if lang == 'sw':
                continue_prompt = f"{conversation_display}\n\n📝 Swali lingine au 0 kumaliza:"
            else:
                continue_prompt = f"{conversation_display}\n\n📝 Another question or 0 to exit:"
            
            # Continue the conversation
            return f"CON {continue_prompt}"
            
        except Exception as e:
            print(f"❌ AI Chat Error: {str(e)}")
            # If AI completely fails, inform user
            if lang == 'sw':
                return "END AI haiwezi kufanya kazi sasa. Enda hospitalini kama ni dharura."
            else:
                return "END AI unavailable now. Go to hospital if emergency."
    
    def _build_conversation_display(self, user_message, ai_response, lang):
        """Build a display showing current conversation exchange within USSD character limits"""
        
        # USSD has ~160 character limit, so we need to be very concise
        max_display_length = 120  # Leave room for prompts
        
        # Start with current exchange
        if lang == 'sw':
            current_exchange = f"Wewe: {user_message}\nAI: {ai_response}"
        else:
            current_exchange = f"You: {user_message}\nAI: {ai_response}"
        
        # If current exchange fits within limit, show it
        if len(current_exchange) <= max_display_length:
            return current_exchange
        
        # If too long, truncate AI response
        available_space = max_display_length - len(f"You: {user_message}\nAI: ")
        if lang == 'sw':
            available_space = max_display_length - len(f"Wewe: {user_message}\nAI: ")
        
        if available_space > 20:
            truncated_response = ai_response[:available_space-3] + "..."
            if lang == 'sw':
                return f"Wewe: {user_message}\nAI: {truncated_response}"
            else:
                return f"You: {user_message}\nAI: {truncated_response}"
        
        # If still too long, show only AI response
        if len(ai_response) <= max_display_length:
            return f"AI: {ai_response}"
        else:
            return f"AI: {ai_response[:max_display_length-7]}..."
    
    def _handle_emergency(self, user):
        """Handle emergency situations with immediate guidance"""
        lang = user.preferred_language
        
        if lang == 'sw':
            emergency_msg = (
                "🚨 MSAADA WA HARAKA 🚨\n\n"
                "PIGA SASA HIVI:\n"
                "• 911 - Dharura\n"
                "• 999 - Ambulensi\n"
                "• 0700000000 - Hospitali\n\n"
                "Dalili za hatari:\n"
                "• Damu nyingi\n"
                "• Maumivu makali\n"
                "• Kupoteza fahamu\n"
                "• Mwanga mkali\n\n"
                "ENDA HOSPITALI SASA!"
            )
        else:
            emergency_msg = (
                "🚨 EMERGENCY HELP 🚨\n\n"
                "CALL IMMEDIATELY:\n"
                "• 911 - Emergency\n"
                "• 999 - Ambulance\n"
                "• 0700000000 - Hospital\n\n"
                "Danger signs:\n"
                "• Heavy bleeding\n"
                "• Severe pain\n"
                "• Loss of consciousness\n"
                "• Bright flashes\n\n"
                "GO TO HOSPITAL NOW!"
            )
        
        # Trigger emergency alert
        self._trigger_emergency_alert(user)
        
        return f"END {emergency_msg}"
    
    def _get_error_response(self, user):
        """Get error response in user's language"""
        lang = getattr(user, 'preferred_language', 'en')
        if lang == 'sw':
            return "END Kuna tatizo. Jaribu tena au piga 911 kama ni dharura."        
        else:
            return "END There was an error. Please try again or call 911 if emergency."
    
    def _get_active_pregnancy(self, user):
        """Get user's active pregnancy"""
        return Pregnancy.query.filter_by(user_id=user.id, is_active=True).first()
    
    def _get_or_create_user(self, phone_number):
        """Get existing user or create new one"""
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            user = User(
                phone_number=phone_number,
                preferred_language=None,  # Will be set during registration
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
        return user
    
    def _clean_phone_number(self, phone_number):
        """Clean and standardize phone number"""
        clean = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        if not clean.startswith('+'):
            if clean.startswith('0'):
                clean = '+254' + clean[1:]
            elif clean.startswith('254'):
                clean = '+' + clean
            else:
                clean = '+254' + clean
        
        return clean
    
    def _trigger_emergency_alert(self, user):
        """Trigger emergency alert and notifications"""
        try:
            from src.services.sms_service import SMSService
            sms_service = SMSService()
            
            if hasattr(user, 'emergency_contact') and user.emergency_contact:
                emergency_msg = f"EMERGENCY: {user.name or user.phone_number} has triggered an emergency alert through MAMA-AI. Please check on them immediately."
                sms_service.send_sms(user.emergency_contact, emergency_msg)
        except Exception as e:
            print(f"Emergency alert failed: {str(e)}")
    
    def _log_message(self, phone_number, msg_type, direction, content, session_id=None):
        """Log USSD message"""
        try:
            log = MessageLog(
                phone_number=phone_number,
                message_type=msg_type,
                direction=direction,
                content=content,
                session_id=session_id
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            print(f"Message logging failed: {str(e)}")
