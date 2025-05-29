"""
KEY CHANGES I MADE - PART 2
===========================

2. SIMPLE SMS HANDLER (handles rate limits with fallback responses):
"""

def handle_incoming_sms_simple(self, from_number, to_number, text, received_at):
    """Simplified SMS handler with immediate fallback responses"""
    try:
        # Clean phone number
        clean_phone = self._clean_phone_number(from_number)
        
        # Log incoming SMS
        self._log_message(clean_phone, "SMS", "incoming", text)
        
        # Get or create user
        user = self._get_or_create_user(clean_phone)
        
        print(f"\n📱 INCOMING SMS (SIMPLE MODE):")
        print(f"📱 From: {clean_phone}")
        print(f"📝 Message: {text}")
        print(f"🕒 Received at: {received_at}")
        
        # Get immediate fallback response (skip AI due to rate limits)
        response = self._get_fallback_response(text.strip(), user)
        
        print(f"\n🤖 SENDING FALLBACK RESPONSE:")
        print(f"📝 Response: {response}")
        
        # Send response SMS back to user using DIRECT API
        sms_result = self.send_sms_direct_api(clean_phone, response)
        
        if sms_result and sms_result.get("status") == "success":
            print(f"✅ SMS Response sent successfully!")
            return {"status": "processed", "response_sent": True, "message": "SMS processed and response sent"}
        else:
            print(f"❌ Failed to send SMS response: {sms_result}")
            return {"status": "processed", "response_sent": False, "message": "SMS processed but response failed"}
            
    except Exception as e:
        print(f"❌ Error in simple SMS handler: {str(e)}")
        return {"status": "error", "message": str(e)}

def _get_fallback_response(self, user_message, user):
    """Get a safe fallback response when AI is filtered or fails"""
    user_message = user_message.lower()
    
    # Swahili greetings
    if any(word in user_message for word in ['habari', 'hujambo', 'mambo', 'salama']):
        return "Habari yako! Mimi ni MAMA-AI. Nipo hapa kukusaidia na maswali ya afya ya mama na mtoto. Uliza chochote! 🤱"
    
    # English greetings
    if any(word in user_message for word in ['hello', 'hi', 'hey', 'good', 'start']):
        return "Hello! I'm MAMA-AI, your maternal health assistant. I'm here to help with pregnancy and maternal health questions. Ask me anything! 👋"
    
    # Health-related fallbacks
    if any(word in user_message for word in ['mgonjwa', 'sick', 'pain', 'dawa', 'health', 'maumivu']):
        return "I understand you have health concerns. For emergencies, please visit a hospital immediately. For health advice, consult with a doctor. 🏥"
    
    # Pregnancy-related fallbacks  
    if any(word in user_message for word in ['mimba', 'pregnancy', 'pregnant', 'baby', 'mtoto']):
        return "For pregnancy-related questions, I recommend consulting with a healthcare provider. Regular prenatal care is important for you and your baby! 👶"
    
    # Default response
    return "Hello! I'm MAMA-AI. I help with maternal health questions. Please ask me about pregnancy, prenatal care, or women's health. For emergencies, contact a doctor immediately! 💙"
