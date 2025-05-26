import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class LanguageDetector:
    def __init__(self):
        self.swahili_keywords = [
            'habari', 'mambo', 'salam', 'shikamoo', 'hujambo',
            'maumivu', 'damu', 'mtoto', 'mama', 'daktari',
            'hospitali', 'ugonjwa', 'afya', 'maji', 'chakula',
            'ujauzito', 'mimba', 'kujifungua', 'kitanda',
            'dawa', 'vidole', 'miguu', 'kichwa', 'tumbo'
        ]
        
        self.english_keywords = [
            'hello', 'hi', 'good', 'morning', 'afternoon',
            'pain', 'blood', 'baby', 'mother', 'doctor',
            'hospital', 'sick', 'health', 'water', 'food',
            'pregnancy', 'pregnant', 'delivery', 'birth',
            'medicine', 'fingers', 'legs', 'head', 'stomach'
        ]
    
    def detect_language(self, text):
        """Detect language of input text"""
        if not text:
            return 'en'
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        swahili_count = sum(1 for word in words if word in self.swahili_keywords)
        english_count = sum(1 for word in words if word in self.english_keywords)
        
        if swahili_count > english_count:
            return 'sw'
        else:
            return 'en'
    
    def get_confidence(self, text, detected_lang):
        """Get confidence score for language detection"""
        if not text:
            return 0.5
        
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.5
        
        if detected_lang == 'sw':
            matches = sum(1 for word in words if word in self.swahili_keywords)
        else:
            matches = sum(1 for word in words if word in self.english_keywords)
        
        return min(matches / len(words), 1.0)

def get_translation(language, key, default_text):
    """Get translation for a given key and language"""
    translations = {
        'en': {
            'main_menu': "Welcome to MAMA-AI 🤱\n1. Pregnancy Tracking\n2. Health Check\n3. Appointments\n4. Emergency\n5. Settings\n6. Get Help",
            'pregnancy_menu': "Pregnancy Tracking\n1. Update symptoms\n2. Track baby's movement\n3. Nutrition tips\n4. Weekly info\n0. Back",
            'health_menu': "Health Check 🏥\n1. Report symptoms\n2. Ask health question\n3. Emergency symptoms\n4. Medication reminder\n0. Back",
            'appointments_menu': "Appointments 📅\n1. View next appointment\n2. Schedule appointment\n3. Appointment history\n0. Back",
            'settings_menu': "Settings ⚙️\n1. Change language\n2. Update profile\n3. Emergency contacts\n0. Back",
            'help_text': "MAMA-AI Help 📖\nThis service provides:\n• Pregnancy tracking\n• Health advice\n• Emergency support\n• Appointment reminders\n\nFor emergencies, dial 911\nSMS 'HELP' for more info",
            'invalid_choice': "Invalid choice. Please try again.",
            'enter_symptoms': "Please describe your current symptoms:",
            'baby_movement': "How many times did you feel baby move in the last hour?\n1. Less than 3\n2. 3-5 times\n3. More than 5",
            'report_symptoms': "Describe your symptoms in detail:",
            'ask_question': "What health question do you have?",
            'choose_language': "Choose language:\n1. English\n2. Kiswahili",
            'update_profile': "Enter your name:",
            'language_changed': "Language updated successfully!",
            'name_updated': "Name updated successfully!",
            'invalid_option': "Invalid option selected.",
            'emergency_response': "🚨 EMERGENCY DETECTED 🚨\n\nIf life-threatening:\nCALL 911 IMMEDIATELY\n\nCommon pregnancy emergencies:\n• Severe bleeding\n• Severe abdominal pain\n• Vision problems\n• Severe headaches\n\nWe're sending your emergency contact a message.\n\nStay calm and seek immediate medical help.",
            'no_pregnancy': "No active pregnancy found.\n1. Register new pregnancy\n0. Back to main menu",
            'sms_help': "MAMA-AI Help 📱\n\nSMS Commands:\n• HELP - This help message\n• SYMPTOMS - Report symptoms\n• APPOINTMENT - Check appointments\n• REMINDER - Set medication reminder\n• EMERGENCY - Get emergency help\n• STOP - Unsubscribe\n\nUSSD: Dial *123# for full menu\n\nEmergency: Call 911",
            'unsubscribed': "You have been unsubscribed from MAMA-AI messages. SMS START to reactivate. For emergencies, always call 911.",
            'welcome_back': "Welcome back to MAMA-AI! 🤱\n\nYour maternal health assistant is now active.\n\nDial *123# for the full menu or SMS HELP for commands.\n\nWe're here to support you through your pregnancy journey!",
            'next_appointment': "Your next appointment:\n📅 {date}\n🏥 {type}\n📍 {location}\n\nWe'll send you a reminder 24 hours before.",
            'no_appointments': "You have no scheduled appointments. Contact your healthcare provider to schedule your next visit.",
            'reminder_info': "Medication Reminders 💊\n\nTo set up reminders:\n1. Dial *123# → Appointments\n2. Visit your healthcare provider\n3. We'll automatically set reminders\n\nFor immediate medication questions, consult your healthcare provider.",
            'appointment_reminder': "📅 APPOINTMENT REMINDER\n\nYou have an appointment tomorrow:\n🕒 {date}\n🏥 {type}\n📍 {location}\n\nPlease arrive 15 minutes early. Bring your pregnancy book and any questions."
        },
        'sw': {
            'main_menu': "Karibu MAMA-AI 🤱\n1. Kufuatilia Ujauzito\n2. Uchunguzi wa Afya\n3. Miadi\n4. Dharura\n5. Mipangilio\n6. Kupata Msaada",
            'pregnancy_menu': "Kufuatilia Ujauzito\n1. Sasisha dalili\n2. Fuatilia mzunguko wa mtoto\n3. Mapendekezo ya lishe\n4. Habari za wiki\n0. Rudi",
            'health_menu': "Uchunguzi wa Afya 🏥\n1. Ripoti dalili\n2. Uliza swali la afya\n3. Dalili za dharura\n4. Ukumbusho wa dawa\n0. Rudi",
            'appointments_menu': "Miadi 📅\n1. Ona miadi ijayo\n2. Panga miadi\n3. Historia ya miadi\n0. Rudi",
            'settings_menu': "Mipangilio ⚙️\n1. Badilisha lugha\n2. Sasisha wasifu\n3. Anwani za dharura\n0. Rudi",
            'help_text': "Msaada wa MAMA-AI 📖\nHuduma hii inatoa:\n• Kufuatilia ujauzito\n• Ushauri wa afya\n• Msaada wa dharura\n• Ukumbusho wa miadi\n\nKwa dharura, piga 911\nTuma SMS 'HELP' kwa habari zaidi",
            'invalid_choice': "Chaguo si sahihi. Tafadhali jaribu tena.",
            'enter_symptoms': "Tafadhali eleza dalili zako za sasa:",
            'baby_movement': "Ni mara ngapi ulisikia mtoto akizunguka katika saa iliyopita?\n1. Chini ya 3\n2. Mara 3-5\n3. Zaidi ya 5",
            'report_symptoms': "Eleza dalili zako kwa undani:",
            'ask_question': "Una swali gani la afya?",
            'choose_language': "Chagua lugha:\n1. Kiingereza\n2. Kiswahili",
            'update_profile': "Ingiza jina lako:",
            'language_changed': "Lugha imesasishwa kikamilifu!",
            'name_updated': "Jina limesasishwa kikamilifu!",
            'invalid_option': "Chaguo si sahihi.",
            'emergency_response': "🚨 DHARURA IMEGUNDULIWA 🚨\n\nIkiwa ni hatari ya maisha:\nPIGA 911 MARA MOJA\n\nDharura za kawaida za ujauzito:\n• Kutokwa damu kwingi\n• Maumivu makali ya tumbo\n• Matatizo ya macho\n• Maumivu makali ya kichwa\n\nTunatuma ujumbe kwa anayekuhudumia.\n\nTulia na tafuta msaada wa haraka.",
            'no_pregnancy': "Hakuna ujauzito unaoendelea. \n1. Sajili ujauzito mpya\n0. Rudi menyu kuu",
            'sms_help': "Msaada wa MAMA-AI 📱\n\nAmri za SMS:\n• HELP - Ujumbe huu wa msaada\n• SYMPTOMS - Ripoti dalili\n• APPOINTMENT - Angalia miadi\n• REMINDER - Weka ukumbusho wa dawa\n• EMERGENCY - Pata msaada wa dharura\n• STOP - Acha kujisajili\n\nUSSD: Piga *123# kwa menyu kamili\n\nDharura: Piga 911",
            'unsubscribed': "Umeacha kujisajili kutoka kwa ujumbe wa MAMA-AI. Tuma SMS START kuanzisha tena. Kwa dharura, daima piga 911.",
            'welcome_back': "Karibu tena MAMA-AI! 🤱\n\nMsaidizi wako wa afya ya mama sasa ni hai.\n\nPiga *123# kwa menyu kamili au tuma SMS HELP kwa amri.\n\nTuko hapa kukusaidia katika safari yako ya ujauzito!",
            'next_appointment': "Miadi yako ijayo:\n📅 {date}\n🏥 {type}\n📍 {location}\n\nTutakutumia ukumbusho masaa 24 kabla.",
            'no_appointments': "Huna miadi iliyopangwa. Wasiliana na mtoa huduma za afya kupanga ziara yako ijayo.",
            'reminder_info': "Ukumbusho wa Dawa 💊\n\nKuweka ukumbusho:\n1. Piga *123# → Miadi\n2. Tembelea mtoa huduma za afya\n3. Tutaweka ukumbusho kiotomatiki\n\nKwa maswali ya haraka ya dawa, shauri na mtoa huduma za afya.",
            'appointment_reminder': "📅 UKUMBUSHO WA MIADI\n\nUna miadi kesho:\n🕒 {date}\n🏥 {type}\n📍 {location}\n\nTafadhali fika dakika 15 mapema. Lete kitabu chako cha ujauzito na maswali yoyote."
        }
    }
    
    return translations.get(language, {}).get(key, default_text)

def translate_text(text, target_language):
    """Simple text translation using keyword mapping"""
    if target_language == 'en':
        return text  # Assume input is already English or mixed
    
    # Simple Swahili translations for common terms
    translations = {
        'hello': 'halo',
        'thank you': 'asante',
        'welcome': 'karibu',
        'help': 'msaada',
        'emergency': 'dharura',
        'pregnancy': 'ujauzito',
        'baby': 'mtoto',
        'mother': 'mama',
        'doctor': 'daktari',
        'hospital': 'hospitali',
        'pain': 'maumivu',
        'bleeding': 'kutokwa damu',
        'appointment': 'miadi',
        'medicine': 'dawa',
        'health': 'afya',
        'symptoms': 'dalili'
    }
    
    # Simple word replacement (in a real app, use proper translation API)
    translated = text.lower()
    for en_word, sw_word in translations.items():
        translated = translated.replace(en_word, sw_word)
    
    return translated

def format_phone_number(phone_number, country_code='+254'):
    """Format phone number to international format"""
    # Remove all non-digit characters except +
    clean = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    
    # Add country code if not present
    if not clean.startswith('+'):
        if clean.startswith('0'):
            clean = country_code + clean[1:]
        elif clean.startswith('254'):
            clean = '+' + clean
        else:
            clean = country_code + clean
    
    return clean

def validate_phone_number(phone_number):
    """Validate phone number format"""
    clean = format_phone_number(phone_number)
    # Basic validation for Kenyan numbers
    return len(clean) >= 12 and clean.startswith('+254')

def extract_keywords(text, language='en'):
    """Extract important keywords from text"""
    try:
        # Download required NLTK data if not available
        try:
            stopwords.words('english')
        except LookupError:
            nltk.download('stopwords')
            nltk.download('punkt')
        
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        
        # Filter out stopwords and get important keywords
        keywords = [word for word in tokens if word.isalpha() and word not in stop_words]
        
        return keywords[:10]  # Return top 10 keywords
    except:
        # Fallback to simple word splitting if NLTK fails
        words = text.lower().split()
        return [word for word in words if len(word) > 3][:10]

def get_emergency_keywords():
    """Get list of emergency keywords in both languages"""
    emergency_keywords = {
        'en': [
            'emergency', 'urgent', 'help', 'bleeding', 'severe pain',
            'can\'t breathe', 'unconscious', 'dizzy', 'blurred vision',
            'heavy bleeding', 'severe headache', 'chest pain', 'fever',
            'vomiting blood', 'water broke', 'contractions'
        ],
        'sw': [
            'dharura', 'haraka', 'msaada', 'damu', 'maumivu makali',
            'sijui kupumua', 'amezimia', 'kizunguzungu', 'macho haoni',
            'damu nyingi', 'maumivu ya kichwa', 'maumivu ya kifua', 'homa',
            'kutapika damu', 'maji yamevunjika', 'uchungu wa kujifungua'
        ]
    }
    
    return emergency_keywords

def is_emergency_message(text):
    """Check if message contains emergency keywords"""
    text_lower = text.lower()
    emergency_keywords = get_emergency_keywords()
    
    # Check both English and Swahili emergency keywords
    for lang_keywords in emergency_keywords.values():
        for keyword in lang_keywords:
            if keyword in text_lower:
                return True
    
    return False

def clean_text(text):
    """Clean and normalize text input"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\?\!\-]', '', text)
    
    return text.strip()

def get_language_name(lang_code):
    """Get full language name from code"""
    languages = {
        'en': 'English',
        'sw': 'Kiswahili'
    }
    return languages.get(lang_code, 'English')
