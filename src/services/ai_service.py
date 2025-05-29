import re
from datetime import datetime
from src.models import User, Pregnancy, EmergencyAlert

class AIService:
    def __init__(self):
        self.emergency_keywords = [
            'severe bleeding', 'heavy bleeding', 'damu nyingi', 'bleeding heavily',
            'severe pain', 'maumivu makali', 'unbearable pain', 'sharp pain',
            'can\'t breathe', 'difficulty breathing', 'sijui kupumua',
            'vision problems', 'blurred vision', 'miwani', 'can\'t see',
            'severe headache', 'maumivu ya kichwa', 'head pounding',
            'fever', 'homa', 'high temperature', 'hot',
            'vomiting blood', 'kutapika damu', 'blood in vomit',
            'water broke', 'maji yamevunjika', 'waters breaking'
        ]
        
        self.high_risk_symptoms = [
            'bleeding', 'spotting', 'cramping', 'contractions',
            'reduced movement', 'no movement', 'swelling',
            'headache', 'dizziness', 'nausea', 'vomiting'
        ]
    
    def analyze_symptoms(self, symptoms_text, user):
        """Analyze symptoms and provide appropriate response"""
        symptoms_lower = symptoms_text.lower()
        
        # Check for emergency symptoms
        emergency_detected = any(keyword in symptoms_lower for keyword in self.emergency_keywords)
        
        if emergency_detected:
            return self._handle_emergency_symptoms(symptoms_text, user)
        
        # Check for high-risk symptoms
        high_risk = any(keyword in symptoms_lower for keyword in self.high_risk_symptoms)
        
        if high_risk:
            return self._handle_high_risk_symptoms(symptoms_text, user)
        
        # Normal symptoms guidance
        return self._handle_normal_symptoms(symptoms_text, user)
    
    def _handle_emergency_symptoms(self, symptoms, user):
        """Handle emergency symptoms"""
        # Create emergency alert
        from src.models import db
        alert = EmergencyAlert(
            user_id=user.id,
            alert_type='severe_symptoms',
            symptoms_reported=symptoms,
            severity_score=9,
            action_taken='emergency_response_sent'
        )
        db.session.add(alert)
        db.session.commit()
        
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "🚨 DHARURA! 🚨\n\n"
                "Dalili hizi ni hatari sana. PIGA simu 911 SASA HIVI au enda hospitali ya karibu.\n\n"
                "Usibaki nyumbani - hii ni dharura ya kiafya.\n\n"
                "Tumetuma ujumbe wa dharura kwa anayekuhudumia."
            )
        else:
            return (
                "🚨 EMERGENCY! 🚨\n\n"
                "These symptoms are very serious. CALL 911 NOW or go to the nearest hospital immediately.\n\n"
                "Do not stay home - this is a medical emergency.\n\n"
                "We've sent an emergency alert to your healthcare provider."
            )
    
    def _handle_high_risk_symptoms(self, symptoms, user):
        """Handle high-risk symptoms"""
        lang = user.preferred_language
        if lang == 'sw':
            return (
                "⚠️ Dalili hizi zinahitaji uchunguzi wa haraka.\n\n"
                "Wasiliana na daktari wako au enda kliniki ndani ya masaa 24.\n\n"
                "Dalili za hatari wakati wa ujauzito:\n"
                "• Kutokwa damu\n"
                "• Maumivu makali\n"
                "• Mzunguko mdogo wa mtoto\n"
                "• Uvimbe mkuu\n\n"
                "Jihadharini na usisubiri."
            )
        else:
            return (
                "⚠️ These symptoms require prompt medical attention.\n\n"
                "Contact your healthcare provider or visit a clinic within 24 hours.\n\n"
                "Warning signs during pregnancy:\n"
                "• Any bleeding\n"
                "• Severe pain\n"
                "• Reduced baby movement\n"
                "• Severe swelling\n\n"
                "Don't wait - seek care promptly."
            )
    
    def _handle_normal_symptoms(self, symptoms, user):
        """Handle normal pregnancy symptoms"""
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
            user_id=user.id, 
            is_active=True
        ).first()

    def chat_with_ai(self, message, user, conversation_history=None):
        """Main chat interface with AI"""
        # Store conversation in session/database if needed
        response = self.process_free_text_query(message, user)
        
        # Log the conversation
        self._log_conversation(user, message, response)
        
        return response
    
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

    def generate_voice_response(self, user_input, user_context, conversation_history=None):
        """Generate AI response specifically optimized for voice interactions"""
        try:
            # Extract user info
            user = user_context if hasattr(user_context, 'id') else None
            if not user:
                # If user_context is a dict, create a minimal user object for compatibility
                class MockUser:
                    def __init__(self, data):
                        self.name = data.get('name')
                        self.phone_number = data.get('phone')
                        self.preferred_language = data.get('language', 'en')
                        self.id = None
                user = MockUser(user_context)
            
            language = user.preferred_language or 'en'
            
            # Create voice-optimized prompt
            voice_prompt = f"""
You are MAMA-AI, a maternal health assistant responding to a voice call.

User said: "{user_input}"

User context:
- Name: {user.name or 'Not provided'}
- Language: {language}
- Current pregnancy status: {user_context.get('pregnancy', {}) if isinstance(user_context, dict) else 'Unknown'}

Voice response guidelines:
- Keep responses conversational and natural for speech
- Use simple, clear language
- Limit responses to 2-3 sentences for voice clarity
- Be warm and supportive
- If emergency keywords detected, provide immediate guidance
- End with a helpful question or next step

Respond in {language} language (English if 'en', Kiswahili if 'sw').
"""
            
            # Use the existing AI response method
            return self.process_free_text_query(voice_prompt, user)
            
        except Exception as e:
            print(f"Error generating voice response: {str(e)}")
            fallback_msg = "I'm sorry, I didn't catch that. Could you please repeat your question?" if language == 'en' else "Samahani, sikuelewa. Je, unaweza kurudia swali lako?"
            return fallback_msg
