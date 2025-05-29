import os
import re
from datetime import datetime
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from src.models import User, Pregnancy, EmergencyAlert, Conversation, db

class AIService:
    def __init__(self):
        # GitHub AI Configuration
        self.endpoint = "https://models.github.ai/inference"
        self.model = "meta/Llama-4-Scout-17B-16E-Instruct"
        self.token = os.getenv("GITHUB_TOKEN", "")
        
        # Initialize AI client
        try:
            self.client = ChatCompletionsClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.token),
            )
            print("✅ GitHub AI client initialized successfully")
        except Exception as e:
            print(f"⚠️ Failed to initialize GitHub AI client: {str(e)}")
            self.client = None
        
        # Emergency keywords for immediate detection
        self.emergency_keywords = [
            'severe bleeding', 'heavy bleeding', 'damu nyingi', 'bleeding heavily',
            'severe pain', 'maumivu makali', 'unbearable pain', 'sharp pain',
            'can\'t breathe', 'difficulty breathing', 'sijui kupumua',
            'vision problems', 'blurred vision', 'miwani', 'can\'t see',
            'severe headache', 'maumivu ya kichwa', 'head pounding',
            'fever', 'homa', 'high temperature', 'hot',
            'vomiting blood', 'kutapika damu', 'blood in vomit',
            'water broke', 'maji yamevunjika', 'waters breaking',
            'unconscious', 'fainting', 'dizzy', 'emergency', 'dharura'
        ]
    
    def get_system_prompt(self, user, language='en'):
        """Get context-aware system prompt for the AI"""
        # Get user's pregnancy info
        pregnancy_info = ""
        if user.pregnancies:
            active_pregnancy = next((p for p in user.pregnancies if p.is_active), None)
            if active_pregnancy:
                pregnancy_info = f"""
Current pregnancy information:
- Weeks pregnant: {active_pregnancy.weeks_pregnant or 'Not specified'}
- Due date: {active_pregnancy.due_date}
- High risk: {'Yes' if active_pregnancy.is_high_risk else 'No'}
- Health conditions: {active_pregnancy.health_conditions or 'None specified'}
"""
        
        base_prompt = f"""You are MAMA-AI, an AI-powered maternal health assistant specifically designed for pregnant women and new mothers in Kenya and East Africa. 

IMPORTANT CONTEXT:
- User's name: {user.name or 'Not provided'}
- Phone: {user.phone_number}
- Preferred language: {language}
- Location: {user.location or 'Not specified'}
{pregnancy_info}

COMMUNICATION GUIDELINES:
1. ALWAYS respond in {language} (English if 'en', Kiswahili if 'sw')
2. Be warm, supportive, and culturally sensitive
3. Keep responses concise for SMS/USSD (max 160 characters when possible)
4. Use simple, clear language that women with basic education can understand
5. Include relevant emojis to make messages friendly: 🤱 💝 🏥 ⚠️ 🚨

MEDICAL SAFETY:
- For ANY emergency symptoms, immediately recommend seeking medical care
- Never provide specific medication dosages
- Always encourage consulting healthcare providers for serious concerns
- Provide general wellness and pregnancy guidance

EMERGENCY KEYWORDS to watch for:
- Heavy bleeding, severe pain, vision problems, severe headache, fever, vomiting blood, water breaking
- Kiswahili equivalents: damu nyingi, maumivu makali, miwani, maumivu ya kichwa, homa, kutapika damu, maji yamevunjika

RESPONSE FORMAT for different scenarios:
- Normal advice: Supportive guidance with practical tips
- Concerning symptoms: Suggest monitoring and when to seek care
- Emergency symptoms: Immediate action needed + emergency contact

Remember: You're supporting women who may have limited healthcare access, so your guidance could be crucial for their wellbeing."""

        return base_prompt
    
    def chat_with_ai(self, user_message, user, session_id=None, channel='SMS'):
        """Main function to chat with GitHub AI models"""
        try:
            # Detect language
            language = self._detect_language(user_message, user.preferred_language)
            
            # Check for immediate emergencies first
            if self._is_emergency_message(user_message):
                return self._handle_emergency_response(user_message, user, session_id, channel, language)
            
            # Get system prompt with context
            system_prompt = self.get_system_prompt(user, language)
            
            # Get recent conversation history for context
            recent_conversations = self._get_recent_conversations(user.id, limit=5)
            context_messages = [SystemMessage(system_prompt)]
            
            # Add conversation history
            for conv in recent_conversations:
                context_messages.append(UserMessage(conv.user_message))
                context_messages.append(SystemMessage(f"Previous AI response: {conv.ai_response}"))
            
            # Add current message
            context_messages.append(UserMessage(user_message))
              # Call GitHub AI - ALWAYS use AI, no fallback
            if not self.client:
                # Re-initialize client if it failed before
                try:
                    self.client = ChatCompletionsClient(
                        endpoint=self.endpoint,
                        credential=AzureKeyCredential(self.token),
                    )
                    print("✅ GitHub AI client re-initialized successfully")
                except Exception as e:
                    print(f"❌ CRITICAL: AI client failed to initialize: {str(e)}")
                    raise Exception(f"AI service unavailable: {str(e)}")
            
            # Make AI call
            response = self.client.complete(
                messages=context_messages,
                temperature=0.7,
                top_p=0.9,
                max_tokens=300,  # Limit for SMS/USSD
                model=self.model
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Post-process response for SMS/USSD
            ai_response = self._format_response_for_channel(ai_response, channel)
            
            # Detect intent and confidence
            intent, confidence = self._detect_intent(user_message)
            
            # Save conversation to database
            self._save_conversation(
                user_id=user.id,
                session_id=session_id,
                channel=channel,
                user_message=user_message,
                ai_response=ai_response,
                intent=intent,
                confidence=confidence,
                language=language
            )
            
            return ai_response
            
        except Exception as e:
            print(f"Error in AI chat: {str(e)}")
            # Return fallback response
            return self._get_error_response(user.preferred_language)
    
    def _is_emergency_message(self, message):
        """Quick check for emergency keywords"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.emergency_keywords)
    
    def _handle_emergency_response(self, user_message, user, session_id, channel, language):
        """Handle emergency situations immediately"""
        # Create emergency alert
        alert = EmergencyAlert(
            user_id=user.id,
            alert_type='emergency_message',
            symptoms_reported=user_message,
            severity_score=9,
            action_taken='emergency_response_sent'
        )
        db.session.add(alert)
        db.session.commit()
        
        if language == 'sw':
            response = (
                "🚨 DHARURA! 🚨\n"
                "Dalili hizi ni hatari sana.\n"
                "ENDA HOSPITALI SASA HIVI!\n"
                "Piga: 911 au 0700000000\n"
                "Usisubiri - hii ni dharura."
            )
        else:
            response = (
                "🚨 EMERGENCY! 🚨\n"
                "These symptoms are serious.\n"
                "GO TO HOSPITAL NOW!\n"
                "Call: 911 or 0700000000\n"
                "Don't wait - this is urgent."
            )
        
        # Save emergency conversation
        self._save_conversation(
            user_id=user.id,
            session_id=session_id,
            channel=channel,
            user_message=user_message,
            ai_response=response,
            intent='emergency',
            confidence=0.95,
            language=language
        )
        
        return response
    
    def _detect_language(self, message, preferred_lang):
        """Simple language detection"""
        swahili_words = ['nina', 'mimi', 'niko', 'je', 'ni', 'wa', 'ya', 'na', 'la', 'maumivu', 'dalili', 'ujauzito']
        message_lower = message.lower()
        
        swahili_count = sum(1 for word in swahili_words if word in message_lower)
        
        if swahili_count >= 2:
            return 'sw'
        elif preferred_lang:
            return preferred_lang
        else:
            return 'en'
    
    def _detect_intent(self, message):
        """Detect user intent from message"""
        message_lower = message.lower()
        
        intents = {
            'symptoms': ['pain', 'hurt', 'sick', 'fever', 'bleeding', 'nausea', 'maumivu', 'dalili', 'homa'],
            'appointment': ['appointment', 'clinic', 'doctor', 'visit', 'miadi', 'daktari', 'hospitali'],
            'pregnancy_info': ['weeks', 'pregnant', 'baby', 'due', 'ujauzito', 'mtoto', 'mimba'],
            'medication': ['medicine', 'pills', 'medication', 'dose', 'dawa', 'vidonge'],
            'emergency': self.emergency_keywords,
            'general': ['help', 'info', 'question', 'msaada', 'habari']
        }
        
        for intent, keywords in intents.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > 0:
                confidence = min(matches / len(keywords) * 2, 1.0)  # Max confidence 1.0
                return intent, confidence
        
        return 'general', 0.5
    
    def _format_response_for_channel(self, response, channel):
        """Format AI response for SMS or USSD constraints"""
        if channel == 'SMS':
            # SMS has 160 character limit per message
            if len(response) > 150:
                # Find a good break point
                if '.' in response:
                    sentences = response.split('.')
                    short_response = sentences[0] + '.'
                    if len(short_response) <= 150:
                        return short_response
                
                # If no good break point, truncate with ellipsis
                return response[:147] + "..."
        
        elif channel == 'USSD':
            # USSD has different constraints
            if len(response) > 180:
                return response[:177] + "..."
        
        return response
    
    def _get_recent_conversations(self, user_id, limit=5):
        """Get recent conversation history for context"""
        return Conversation.query.filter_by(user_id=user_id)\
                               .order_by(Conversation.created_at.desc())\
                               .limit(limit).all()
    
    def _save_conversation(self, user_id, session_id, channel, user_message, ai_response, 
                          intent, confidence, language):
        """Save conversation to database"""
        try:
            conversation = Conversation(
                user_id=user_id,
                session_id=session_id,
                channel=channel,
                user_message=user_message,
                ai_response=ai_response,
                intent_detected=intent,
                confidence_score=confidence,
                language_detected=language
            )
            db.session.add(conversation)
            db.session.commit()
        except Exception as e:
            print(f"Error saving conversation: {str(e)}")
            db.session.rollback()
    
    def _get_ai_emergency_response(self, message, user, language):
        """Get AI-powered emergency response - NO hardcoding"""
        try:
            emergency_prompt = f"""
EMERGENCY SITUATION DETECTED!

User message: "{message}"
User's pregnancy week: {self._get_pregnancy_weeks(user)}
Language: {language}

Provide IMMEDIATE emergency guidance:
1. Assess severity (1-10 scale)
2. Immediate actions to take
3. When to call emergency services
4. Hospital contact info if needed

Respond in {language} language. Be direct and urgent but reassuring.
"""
            # Use AI for emergency response too
            return self._get_ai_response_direct(emergency_prompt, user, language)
        except Exception as e:
            print(f"❌ Emergency AI failed: {str(e)}")
            # Only as absolute last resort            return f"🚨 EMERGENCY: Go to hospital NOW! Call emergency services immediately!"
    
    def _get_error_response(self, language, user=None):
        """Get AI-powered error response - NO hardcoding"""
        try:
            if user:
                error_prompt = f"""
There was a technical issue with our system. Please provide a helpful error message to a pregnant woman.

User's language: {language}
Be reassuring but include emergency guidance.

Respond in {language} language (English if 'en', Kiswahili if 'sw').
"""
                return self._get_ai_response_direct(error_prompt, user, language)
            else:
                # Minimal fallback only when absolutely no user context
                if language == 'sw':
                    return "Kuna tatizo. Kama ni dharura, enda hospitali. 🤱"
                else:
                    return "Technical issue. If emergency, go to hospital. 🤱"
        except:
            # Final fallback
            return "Technical error. Seek medical help if urgent. 🤱"
    
    def _get_ai_response_direct(self, prompt, user, language):
        """Get direct AI response for any prompt - ensures AI always responds"""
        try:
            # Ensure client is available
            if not self.client:
                self.client = ChatCompletionsClient(
                    endpoint=self.endpoint,
                    credential=AzureKeyCredential(self.token),
                )
            
            # Create messages
            messages = [
                SystemMessage(self.get_system_prompt(user, language)),
                UserMessage(prompt)
            ]
            
            # Get AI response
            response = self.client.complete(
                messages=messages,
                temperature=0.7,
                top_p=0.9,
                max_tokens=300,
                model=self.model
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Direct AI call failed: {str(e)}")
            raise Exception(f"AI service completely unavailable: {str(e)}")
    
    # Legacy methods for backward compatibility
    def analyze_symptoms(self, symptoms_text, user):
        """Legacy method - now uses AI chat"""
        return self.chat_with_ai(symptoms_text, user, channel='SMS')
    
    def process_free_text_query(self, text, user):
        """Legacy method - now uses AI chat"""
        return self.chat_with_ai(text, user, channel='SMS')
        symptoms_lower = symptoms.lower()
        
        # Common pregnancy discomforts and advice
        if any(word in symptoms_lower for word in ['nausea', 'vomiting', 'morning sickness', 'tapika']):
            return self._nausea_advice(user)
        elif any(word in symptoms_lower for word in ['back pain', 'maumivu ya mgongo', 'backache']):
            return self._back_pain_advice(user)
        elif any(word in symptoms_lower for word in ['tired', 'fatigue', 'uchovu', 'exhausted']):
            return self._fatigue_advice(user)
        elif any(word in symptoms_lower for word in ['heartburn', 'acidity', 'chest burn']):
            return self._heartburn_advice(user)
        else:
            return self._general_advice(user)
    
    def _nausea_advice(self, user):
        """Advice for nausea and morning sickness"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Kuharisha ni kawaida katika miezi ya kwanza ya ujauzito.\n\n"
                "Mapendekezo:\n"
                "• Kula kidogo kidogo mara nyingi\n"
                "• Ongeza maji\n"
                "• Kula biskuti kabla ya kuamka\n"
                "• Epuka vyakula vya kunuka kali\n\n"
                "Wasiliana na daktari ikiwa:\n"
                "• Unatapika sana\n"
                "• Huwezi kula au kunywa\n"
                "• Unapoteza uzito"
            )
        else:
            return (
                "Nausea is common in early pregnancy.\n\n"
                "Tips to help:\n"
                "• Eat small, frequent meals\n"
                "• Stay hydrated\n"
                "• Try crackers before getting up\n"
                "• Avoid strong smells\n\n"
                "Contact your doctor if:\n"
                "• Vomiting is severe\n"
                "• Can't keep food/fluids down\n"
                "• Losing weight"
            )
    
    def _back_pain_advice(self, user):
        """Advice for back pain"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Maumivu ya mgongo ni ya kawaida wakati wa ujauzito.\n\n"
                "Jinsi ya kupunguza:\n"
                "• Vaa viatu visivyo na visigino\n"
                "• Lala upande mwako\n"
                "• Tumia mto wa moto\n"
                "• Fanya mazoezi ya wepesi\n\n"
                "Wasiliana na daktari ikiwa maumivu ni makali au yanaongezeka."
            )
        else:
            return (
                "Back pain is common during pregnancy.\n\n"
                "Ways to reduce it:\n"
                "• Wear flat, comfortable shoes\n"
                "• Sleep on your side\n"
                "• Use a warm compress\n"
                "• Do gentle exercises\n\n"
                "Contact your doctor if pain is severe or worsening."
            )
    
    def _fatigue_advice(self, user):
        """Advice for fatigue"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Uchovu ni wa kawaida wakati wa ujauzito.\n\n"
                "Jinsi ya kushughulikia:\n"
                "• Pumzika mara nyingi\n"
                "• Lala masaa ya kutosha\n"
                "• Kula vyakula vyenye nishati\n"
                "• Fanya mazoezi ya wepesi\n\n"
                "Hakikisha unakula vyema na kunywa maji ya kutosha."
            )
        else:
            return (
                "Fatigue is very common during pregnancy.\n\n"
                "Ways to manage:\n"
                "• Rest frequently\n"
                "• Get adequate sleep\n"
                "• Eat energy-rich foods\n"
                "• Light exercise helps\n\n"
                "Make sure you're eating well and staying hydrated."
            )
    
    def _heartburn_advice(self, user):
        """Advice for heartburn"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Uchungu wa kifuani ni wa kawaida wakati wa ujauzito.\n\n"
                "Mapendekezo:\n"
                "• Kula kidogo kidogo\n"
                "• Epuka vyakula vya kunuka\n"
                "• Usikae mara baada ya kula\n"
                "• Ongeza kichwa chako unapolala\n\n"
                "Wasiliana na daktari kwa dawa salama za ujauzito."
            )
        else:
            return (
                "Heartburn is common during pregnancy.\n\n"
                "Tips to help:\n"
                "• Eat smaller meals\n"
                "• Avoid spicy/acidic foods\n"
                "• Don't lie down after eating\n"
                "• Elevate your head while sleeping\n\n"
                "Talk to your doctor about pregnancy-safe antacids."
            )
    
    def _general_advice(self, user):
        """General pregnancy advice"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Asante kwa kutueleza kuhusu dalili zako.\n\n"
                "Kumbuka:\n"
                "• Tembelea kliniki mara kwa mara\n"
                "• Kula vyakula vyenye lishe\n"
                "• Kunywa maji mengi\n"
                "• Pumzika vizuri\n\n"
                "Wasiliana na daktari wako ikiwa una wasiwasi wowote."
            )
        else:
            return (
                "Thank you for sharing your symptoms with us.\n\n"
                "Remember to:\n"
                "• Attend regular clinic visits\n"
                "• Eat nutritious foods\n"
                "• Stay well hydrated\n"
                "• Get adequate rest\n\n"
                "Contact your healthcare provider if you have any concerns."
            )
    
    def analyze_baby_movement(self, movement_report, user):
        """Analyze baby movement patterns"""
        lang = user.preferred_language
        
        if movement_report == '1':  # Less than 3 movements
            if lang == 'sw':
                return (
                    "⚠️ Mzunguko mdogo wa mtoto unaweza kuwa dalili ya hatari.\n\n"
                    "Fanya hivi:\n"
                    "1. Lala upande wa kushoto\n"
                    "2. Kunywa maji baridi\n"
                    "3. Hesabu mzunguko kwa saa 2\n\n"
                    "Ikiwa bado hamzunguki, ENDA HOSPITALI SASA HIVI!"
                )
            else:
                return (
                    "⚠️ Reduced baby movement may be a warning sign.\n\n"
                    "Try this:\n"
                    "1. Lie on your left side\n"
                    "2. Drink cold water\n"
                    "3. Count movements for 2 hours\n\n"
                    "If still no movement, GO TO HOSPITAL IMMEDIATELY!"
                )
        elif movement_report == '2':  # 3-5 movements
            if lang == 'sw':
                return (
                    "Mzunguko huu ni wa kati. Fuatilia zaidi.\n\n"
                    "Hesabu mzunguko wa mtoto kila siku wakati huo huo.\n\n"
                    "Wasiliana na daktari ikiwa unaona mabadiliko."
                )
            else:
                return (
                    "This movement level is moderate. Keep monitoring.\n\n"
                    "Count baby movements at the same time each day.\n\n"
                    "Contact your doctor if you notice changes."
                )
        else:  # More than 5 movements
            if lang == 'sw':
                return (
                    "✅ Vizuri! Mtoto wako anaonyesha ishara nzuri za afya.\n\n"
                    "Endelea kufuatilia mzunguko wake kila siku."
                )
            else:
                return (
                    "✅ Great! Your baby is showing good signs of health.\n\n"
                    "Continue monitoring movement patterns daily."
                )
    
    def get_nutrition_tips(self, user):
        """Get nutrition tips for pregnant women"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Lishe Muhimu Wakati wa Ujauzito 🥗\n\n"
                "Kula:\n"
                "• Mboga za majani\n"
                "• Matunda\n"
                "• Protini (nyama, samaki, maharage)\n"
                "• Maziwa na mazao yake\n"
                "• Nafaka kamili\n\n"
                "Epuka:\n"
                "• Pombe\n"
                "• Sigara\n"
                "• Kahawa nyingi\n"
                "• Samaki wenye sumu\n\n"
                "Kunywa maji mengi!"
            )
        else:
            return (
                "Essential Pregnancy Nutrition 🥗\n\n"
                "Include:\n"
                "• Leafy green vegetables\n"
                "• Fresh fruits\n"
                "• Protein (meat, fish, beans)\n"
                "• Dairy products\n"
                "• Whole grains\n\n"
                "Avoid:\n"
                "• Alcohol\n"
                "• Smoking\n"
                "• Excessive caffeine\n"
                "• High-mercury fish\n\n"
                "Stay well hydrated!"
            )
    
    def get_weekly_info(self, weeks_pregnant):
        """Get week-specific pregnancy information"""
        if weeks_pregnant <= 12:
            return self._first_trimester_info(weeks_pregnant)
        elif weeks_pregnant <= 28:
            return self._second_trimester_info(weeks_pregnant)
        else:
            return self._third_trimester_info(weeks_pregnant)
    
    def _first_trimester_info(self, weeks):
        return (
            f"Week {weeks} - First Trimester 🌱\n\n"
            "What's happening:\n"
            "• Baby's organs are forming\n"
            "• Morning sickness is common\n"
            "• Fatigue is normal\n\n"
            "Important:\n"
            "• Take folic acid\n"
            "• Avoid alcohol/smoking\n"
            "• Schedule first prenatal visit"
        )
    
    def _second_trimester_info(self, weeks):
        return (
            f"Week {weeks} - Second Trimester 🤗\n\n"
            "What's happening:\n"
            "• Energy may return\n"
            "• Baby bump showing\n"
            "• You may feel baby move\n\n"
            "Important:\n"
            "• Continue prenatal vitamins\n"
            "• Regular checkups\n"
            "• Start thinking about birth plan"
        )
    
    def _third_trimester_info(self, weeks):
        return (
            f"Week {weeks} - Third Trimester 🤰\n\n"
            "What's happening:\n"
            "• Baby is growing rapidly\n"
            "• You may feel uncomfortable\n"
            "• Preparing for birth\n\n"
            "Important:\n"
            "• Monitor baby movements\n"
            "• Pack hospital bag\n"
            "• Know labor signs"
        )
    
    def answer_health_question(self, question, user):
        """Answer general health questions"""
        question_lower = question.lower()
        lang = user.preferred_language
        
        # Common pregnancy questions
        if any(word in question_lower for word in ['safe', 'salama', 'can i', 'naweza']):
            return self._safety_advice(question, user)
        elif any(word in question_lower for word in ['pain', 'maumivu', 'hurt', 'ache']):
            return self._pain_guidance(question, user)
        elif any(word in question_lower for word in ['eat', 'food', 'kula', 'chakula']):
            return self._food_advice(question, user)
        else:
            return self._general_health_advice(user)
    
    def _safety_advice(self, question, user):
        """Safety-related advice"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Kwa usalama wakati wa ujauzito:\n\n"
                "Salama:\n"
                "• Mazoezi ya wepesi\n"
                "• Kukaa upande wa kushoto\n"
                "• Kuoga kwa maji ya joto la kawaida\n\n"
                "Epuka:\n"
                "• Mazoezi makali\n"
                "• Kupanda juu\n"
                "• Maji ya moto sana\n\n"
                "Uliza daktari wako daima!"
            )
        else:
            return (
                "For safety during pregnancy:\n\n"
                "Safe:\n"
                "• Gentle exercise\n"
                "• Sleeping on left side\n"
                "• Warm (not hot) baths\n\n"
                "Avoid:\n"
                "• Intense exercise\n"
                "• High altitudes\n"
                "• Very hot water\n\n"
                "Always ask your doctor!"
            )
    
    def _pain_guidance(self, question, user):
        """Pain-related guidance"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Kuhusu maumivu wakati wa ujauzito:\n\n"
                "Maumivu ya kawaida:\n"
                "• Mgongo\n"
                "• Miguu\n"
                "• Kichwa (kidogo)\n\n"
                "Wasiliana na daktari ikiwa:\n"
                "• Maumivu ni makali\n"
                "• Yanaongezeka\n"
                "• Yana pamoja na dalili nyingine\n\n"
                "Usitumie dawa bila ushauri wa daktari."
            )
        else:
            return (
                "About pain during pregnancy:\n\n"
                "Normal discomforts:\n"
                "• Back pain\n"
                "• Leg cramps\n"
                "• Mild headaches\n\n"
                "Contact doctor if pain is:\n"
                "• Severe\n"
                "• Worsening\n"
                "• With other symptoms\n\n"
                "Don't take medications without consulting your doctor."
            )
    
    def _food_advice(self, question, user):
        """Food and nutrition advice"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Kuhusu chakula wakati wa ujauzito:\n\n"
                "Kula:\n"
                "• Mboga na matunda\n"
                "• Protini\n"
                "• Chakula chenye chuma\n"
                "• Kalisiamu\n\n"
                "Epuka:\n"
                "• Nyama mbichi\n"
                "• Maziwa yasiyochemshwa\n"
                "• Samaki wa kina\n\n"
                "Uliza daktari kuhusu vitamini."
            )
        else:
            return (
                "About food during pregnancy:\n\n"
                "Eat:\n"
                "• Fruits and vegetables\n"
                "• Lean proteins\n"
                "• Iron-rich foods\n"
                "• Calcium sources\n\n"
                "Avoid:\n"
                "• Raw meat/fish\n"
                "• Unpasteurized dairy\n"
                "• High-mercury fish\n\n"
                "Ask your doctor about supplements."
            )
    
    def _general_health_advice(self, user):
        """General health advice"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Kwa maswali ya afya, ni bora kuongea na daktari wako.\n\n"
                "Kila ujauzito ni tofauti. Daktari wako anajua historia yako ya kiafya.\n\n"
                "Usisite kuuliza maswali yoyote wakati wa vizio vyako."
            )
        else:
            return (
                "For specific health questions, it's best to speak with your healthcare provider.\n\n"
                "Every pregnancy is different, and your doctor knows your medical history.\n\n"
                "Don't hesitate to ask questions during your visits."
            )
    
    def process_free_text_query(self, text, user):
        """Process free text queries using simple keyword matching"""
        text_lower = text.lower()
        
        # Check for greetings
        if any(word in text_lower for word in ['hello', 'hi', 'halo', 'mambo', 'habari']):
            return self._greeting_response(user)
        
        # Check for symptoms
        elif any(word in text_lower for word in ['pain', 'bleeding', 'sick', 'maumivu', 'damu']):
            return self.analyze_symptoms(text, user)
        
        # Check for questions about baby
        elif any(word in text_lower for word in ['baby', 'mtoto', 'movement', 'kick']):
            return self._baby_info(user)
        
        # Check for appointment queries
        elif any(word in text_lower for word in ['appointment', 'clinic', 'doctor', 'miadi']):
            return self._appointment_info(user)
        
        # Default response
        else:
            return self._default_response(user)
    
    def _greeting_response(self, user):
        """Greeting response"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                f"Halo {user.name or 'Mama'}! 👋\n\n"
                "Karibu kwenye MAMA-AI. Niko hapa kukusaidia katika safari yako ya ujauzito.\n\n"
                "Je, una swali au ungependa msaada wowote?"
            )
        else:
            return (
                f"Hello {user.name or 'Mama'}! 👋\n\n"
                "Welcome to MAMA-AI. I'm here to support you through your pregnancy journey.\n\n"
                "Do you have any questions or need assistance?"
            )
    
    def _baby_info(self, user):
        """Baby development information"""
        pregnancy = self._get_active_pregnancy(user)
        if pregnancy:
            return self.get_weekly_info(pregnancy.weeks_pregnant or 20)
        else:
            lang = user.preferred_language
            if lang == 'sw':
                return "Tafadhali sajili ujauzito wako ili tupate kutoa ushauri sahihi."
            else:
                return "Please register your pregnancy so we can provide appropriate guidance."
    
    def _appointment_info(self, user):
        """Appointment information"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Kwa habari za miadi:\n\n"
                "• Piga *123*3# kwa miadi yako\n"
                "• Tumia SMS: APPOINTMENT\n"
                "• Tembelea kliniki mara kwa mara\n\n"
                "Ukumbusho wa miadi utatumwa siku 1 kabla."
            )
        else:
            return (
                "For appointment information:\n\n"
                "• Dial *123*3# for your appointments\n"
                "• SMS: APPOINTMENT\n"
                "• Attend regular clinic visits\n\n"
                "Appointment reminders sent 1 day before."
            )
    
    def _default_response(self, user):
        """Default response for unrecognized queries"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "Samahani, sijaelewi swali lako vizuri.\n\n"
                "Unaweza:\n"
                "• Piga *123# kwa menyu kamili\n"
                "• Tuma SMS: HELP\n"
                "• Wasiliana na daktari wako\n\n"
                "Niko hapa kukusaidia!"
            )
        else:
            return (
                "Sorry, I didn't quite understand your question.\n\n"
                "You can:\n"
                "• Dial *123# for full menu\n"
                "• SMS: HELP\n"
                "• Contact your healthcare provider\n\n"
                "I'm here to help!"
            )
    
    def _get_active_pregnancy(self, user):
        """Get user's active pregnancy"""
        from src.models import Pregnancy
        return Pregnancy.query.filter_by(
            user_id=user.id,            is_active=True
        ).first()

    def _log_conversation(self, user, user_message, ai_response):
        """Log conversation for learning and improvement"""
        from src.models import db, MessageLog
        
        # Log user message
        user_log = MessageLog(
            phone_number=user.phone_number,
            message_type='CHAT',
            direction='incoming',
            content=user_message
        )
        db.session.add(user_log)
        
        # Log AI response
        ai_log = MessageLog(
            phone_number=user.phone_number,
            message_type='CHAT',
            direction='outgoing',
            content=ai_response
        )
        db.session.add(ai_log)
        db.session.commit()
