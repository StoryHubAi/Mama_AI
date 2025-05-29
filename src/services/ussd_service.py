import os
import re
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
        """Handle conversational AI chat with optimized response display"""
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
                ai_prompt,
                user,
                session_id=session_key,
                channel='USSD'
            )
            
            # Build optimized conversation display
            conversation_display = self._build_conversation_display(
                user_message, ai_response, lang
            )
            
            # Return the formatted conversation directly (display already includes continuation prompt)
            return f"CON {conversation_display}"
            
        except Exception as e:
            print(f"❌ AI Chat Error: {str(e)}")            # If AI completely fails, inform user
            if lang == 'sw':
                return "END AI haiwezi kufanya kazi sasa. Enda hospitalini kama ni dharura."
            else:
                return "END AI unavailable now. Go to hospital if emergency."
    
    def _build_conversation_display(self, user_message, ai_response, lang):
        """Build a display showing FULL AI response within USSD character limits"""
        
        # USSD limits: Use maximum space (182 chars standard, push to 180)
        max_total_length = 180
        
        # Set up minimal continuation prompts to maximize response space
        if lang == 'sw':
            continue_prompt = "0=Ondoka"
            response_prefix = "🤖 "
        else:
            continue_prompt = "0=Exit"
            response_prefix = "🤖 "
        
        # Calculate maximum space for AI response
        prompt_space = len(f"\n\n{continue_prompt}")
        prefix_space = len(response_prefix)
        available_space = max_total_length - prefix_space - prompt_space - 1  # -1 minimal safety
        
        # Clean the AI response thoroughly
        cleaned_response = self._clean_ai_response(ai_response)
        
        # If response fits completely, use it
        if len(cleaned_response) <= available_space:
            optimized_response = cleaned_response
        else:
            # Smart truncation that preserves maximum medical content
            optimized_response = self._preserve_max_content(cleaned_response, available_space, lang)
        
        return f"{response_prefix}{optimized_response}\n\n{continue_prompt}"
    
    def _optimize_ai_response_for_ussd(self, ai_response, lang):
        """Optimize AI response specifically for USSD constraints"""
        if not ai_response:
            return "No response available." if lang == 'en' else "Hakuna jibu."
        
        # First, try to extract key medical advice
        key_info = self._extract_key_medical_info(ai_response)
        if key_info and len(key_info) <= 120:  # Leave room for prompts
            return key_info
        
        # If no key info extracted, use regular cleaning and truncation
        cleaned = self._clean_ai_response(ai_response)
        if len(cleaned) <= 120:
            return cleaned
        
        # As last resort, create a summary
        return self._create_response_summary(ai_response, lang)
    
    def _extract_key_medical_info(self, response):
        """Extract the most important medical information from AI response"""
        if not response:
            return None
        
        # Look for key medical advice patterns
        key_patterns = [
            # Advice patterns
            r'(?:You should|It\'s recommended|Please|Take|Avoid|Contact|See a doctor)[^.]*\.',
            r'(?:Important|Warning|Urgent|Emergency)[^.]*\.',
            # Symptom patterns  
            r'(?:Symptoms include|Signs include|Watch for)[^.]*\.',
            # Action patterns
            r'(?:Call|Visit|Go to|Seek)[^.]*\.',
        ]
        
        extracted = []
        
        for pattern in key_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            extracted.extend(matches)
        
        if extracted:
            # Join first few key pieces
            key_text = ' '.join(extracted[:2])
            if len(key_text) <= 120:
                return key_text
        
        return None
    
    def _create_response_summary(self, response, lang):
        """Create a concise summary when response is too long"""
        if not response:
            return "No response" if lang == 'en' else "Hakuna jibu"
        
        # Split into sentences
        sentences = response.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return response[:100] + "..." if len(response) > 100 else response
        
        # Try to find the most important sentence (usually first or contains keywords)
        important_keywords = [
            'important', 'urgent', 'should', 'must', 'contact', 'doctor', 
            'hospital', 'immediately', 'muhimu', 'haraka', 'daktari'
        ]
        
        # Look for sentences with important keywords
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in important_keywords):
                if len(sentence) <= 100:
                    return sentence + "."
        
        # If no important sentence found, use first sentence
        first_sentence = sentences[0]
        if len(first_sentence) <= 100:
            return first_sentence + "."
        
        # Last resort: truncate first sentence
        return first_sentence[:97] + "..."
    
    def _clean_ai_response(self, response):
        """Clean AI response by removing excessive formatting and redundant text"""
        if not response:
            return "No response available."
        
        # Remove excessive line breaks and spaces
        cleaned = ' '.join(response.split())
        
        # Remove greeting fluff that wastes space (like "Timo, hello.")
        greeting_patterns = [
            r"^[A-Za-z]+,?\s+hello\.?\s*",  # "Timo, hello." or "Hello."
            r"^Hello,?\s+[A-Za-z]+\.?\s*",   # "Hello, Timo."
            r"^Hi,?\s+[A-Za-z]+\.?\s*",      # "Hi, Timo."
        ]
        
        for pattern in greeting_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        
        # Remove common AI prefixes that waste space
        prefixes_to_remove = [
            "I understand that you're asking about",
            "Thank you for your question about",
            "I'd be happy to help you with",
            "Based on your question,",
            "From a medical perspective,",
            "It's important to note that",
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        # Remove redundant phrases
        redundant_phrases = [
            "Please remember that",
            "It's always recommended to",
            "You should always",
            "Please note that",
            "Keep in mind that",
        ]
        
        for phrase in redundant_phrases:
            cleaned = cleaned.replace(phrase, "")
        
        # Clean up extra spaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def _smart_truncate_response(self, response, max_length, lang):
        """Intelligently truncate response using multiple strategies"""
        
        if len(response) <= max_length:
            return response
        
        # Strategy 1: Try to end at sentence boundary
        truncated = response[:max_length-3]
        sentence_endings = ['. ', '! ', '? ']
        
        best_cut = -1
        for ending in sentence_endings:
            pos = truncated.rfind(ending)
            if pos > best_cut and pos > max_length * 0.6:  # At least 60% of content
                best_cut = pos + 1
        
        if best_cut > 0:
            return response[:best_cut]
        
        # Strategy 2: Try to end at clause boundary (comma, semicolon)
        clause_endings = [', ', '; ']
        for ending in clause_endings:
            pos = truncated.rfind(ending)
            if pos > max_length * 0.7:  # At least 70% of content
                return response[:pos] + "."
        
        # Strategy 3: Try to end at word boundary
        words = response[:max_length-3].split()
        if len(words) > 1:
            # Remove last word if it's incomplete and add ellipsis
            truncated_words = words[:-1]
            result = ' '.join(truncated_words)
            if len(result) < max_length - 3:
                return result + "..."        
        # Strategy 4: Hard truncation with ellipsis
        return response[:max_length-3] + "..."
    
    def _preserve_max_content(self, response, max_length, lang):
        """Preserve maximum content while fitting USSD limits, prioritizing critical info"""
        if len(response) <= max_length:
            return response
        
        # First, check if response contains critical information that must be preserved
        critical_patterns = [
            r'\b0707861787\b',  # Emergency contact
            r'\bemergency\b',   # Emergency keywords
            r'\burgent\b',
            r'\bimmediately\b',
            r'\bhospital\b',
            r'\bdoctor\b',
            r'\bprenatal vitamins\b',  # Important medical terms
            r'\bfolic acid\b',
            r'\biron\b',
            r'\bcalcium\b'
        ]
        
        # Strategy 1: If response contains critical info, try to preserve it
        import re
        critical_info = []
        for pattern in critical_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            critical_info.extend(matches)
        
        if critical_info:
            # Try to extract sentences containing critical information
            sentences = response.replace('!', '.').replace('?', '.').split('.')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            critical_sentences = []
            regular_sentences = []
            
            for sentence in sentences:
                is_critical = any(re.search(pattern, sentence, re.IGNORECASE) for pattern in critical_patterns)
                if is_critical:
                    critical_sentences.append(sentence)
                else:
                    regular_sentences.append(sentence)
            
            # Build response prioritizing critical sentences
            result = ""
            
            # Add critical sentences first
            for sentence in critical_sentences:
                test_result = f"{result} {sentence}.".strip() if result else f"{sentence}."
                if len(test_result) <= max_length:
                    result = test_result
                elif not result:  # If first critical sentence is too long, truncate it smartly
                    return self._smart_sentence_truncate(sentence, max_length)
            
            # Add regular sentences if space remains
            for sentence in regular_sentences:
                test_result = f"{result} {sentence}.".strip() if result else f"{sentence}."
                if len(test_result) <= max_length:
                    result = test_result
                else:
                    break
            
            if result:
                return result
        
        # Strategy 2: Regular sentence-by-sentence preservation
        sentences = response.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        result = ""
        for sentence in sentences:
            # Test if adding this sentence fits
            test_result = f"{result} {sentence}.".strip() if result else f"{sentence}."
            if len(test_result) <= max_length:
                result = test_result
            else:
                # If we have some content, return it
                if result:
                    return result
                # If first sentence is too long, truncate it intelligently
                else:
                    return self._smart_sentence_truncate(sentence, max_length)
        
        return result if result else response[:max_length]
    
    def _smart_sentence_truncate(self, sentence, max_length):
        """Intelligently truncate a single sentence to preserve key medical info"""
        if len(sentence) <= max_length:
            return sentence
        
        # Look for key medical terms to preserve
        medical_keywords = [
            'take', 'avoid', 'contact', 'doctor', 'hospital', 'emergency',
            'rest', 'drink', 'eat', 'medicine', 'treatment', 'symptoms'
        ]
          # Try to find a good breaking point that keeps medical advice
        words = sentence.split()
        result = ""
        
        for word in words:
            test_result = f"{result} {word}".strip() if result else word
            if len(test_result) <= max_length - 3:  # Leave space for "..."
                result = test_result
            else:
                break
        
        # Add ellipsis if we truncated
        if len(result) < len(sentence):
            return result + "..."
        
        return result
    
    def _log_message(self, phone_number, channel, direction, content, session_id=None):
        """Log USSD messages to database"""
        try:
            # Get or create user
            user = self._get_or_create_user(phone_number)
            
            # Create message log entry
            log_entry = MessageLog(
                user_id=user.id,
                phone_number=phone_number,
                channel=channel,
                direction=direction,
                content=content,
                session_id=session_id,
                created_at=datetime.utcnow()
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
            print(f"📝 USSD Log: {direction.upper()} - {phone_number} - {content[:50]}...")
            
        except Exception as e:
            print(f"❌ USSD Logging Error: {str(e)}")
    
    def _clean_phone_number(self, phone_number):
        """Clean and standardize phone number format"""
        if not phone_number:
            return None
        
        # Remove any non-digit characters
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Handle Kenyan numbers
        if clean_number.startswith('254'):
            return f"+{clean_number}"
        elif clean_number.startswith('0'):
            return f"+254{clean_number[1:]}"
        elif len(clean_number) == 9:  # 7XXXXXXXX format
            return f"+254{clean_number}"
        
        return f"+{clean_number}"
    
    def _get_or_create_user(self, phone_number):
        """Get existing user or create new one"""
        try:
            user = User.query.filter_by(phone_number=phone_number).first()
            if not user:
                user = User(phone_number=phone_number)
                db.session.add(user)
                db.session.commit()
            return user
        except Exception as e:
            print(f"❌ User creation error: {str(e)}")
            db.session.rollback()
            # Return a temporary user object for error cases
            return User(phone_number=phone_number)
    
    def _get_active_pregnancy(self, user):
        """Get user's active pregnancy record"""
        try:
            return Pregnancy.query.filter_by(
                user_id=user.id,
                is_active=True
            ).first()
        except Exception as e:
            print(f"❌ Pregnancy query error: {str(e)}")
            return None
    
    def _get_error_response(self, user):
        """Get appropriate error response based on user language"""
        lang = user.preferred_language if user and user.preferred_language else 'en'
        
        if lang == 'sw':
            return "END Kuna hitilafu. Jaribu tena baadaye."
        else:
            return "END System error. Please try again later."
