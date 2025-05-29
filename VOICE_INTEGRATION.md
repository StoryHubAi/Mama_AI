# MAMA-AI Voice Integration Guide

This guide will help you set up and test Africa's Talking Voice API integration for the MAMA-AI project.

## Overview

The voice integration allows users to interact with MAMA-AI through phone calls using:
- **DTMF (Touch-tone) inputs**: Users press number keys for menu navigation
- **Voice recordings**: Users can speak their symptoms or concerns
- **Text-to-Speech responses**: MAMA-AI responds with spoken messages

## Prerequisites

1. **Africa's Talking Account**: You need a voice-enabled account
2. **Voice Phone Number**: Purchase a voice number from Africa's Talking
3. **Public URL**: Your application needs to be accessible via HTTPS for callbacks

## Files Created/Modified

### New Files:
- `src/services/voice_service.py` - Voice service handling logic
- `test_voice.py` - Python test script
- `test_voice.ps1` - PowerShell test script
- `VOICE_INTEGRATION.md` - This documentation

### Modified Files:
- `app.py` - Added voice endpoints (`/voice`, `/make_call`)

## Voice Service Features

### 1. Main Voice Menu
When users call the MAMA-AI number, they hear:
```
"Welcome to MAMA-AI, your maternal health assistant. 
Press 1 for pregnancy symptoms, 
Press 2 for appointment reminders, 
Press 3 for emergency assistance, 
Press 9 to speak with our AI assistant."
```

### 2. DTMF Navigation
- **1**: Pregnancy symptoms tracking
- **2**: Appointment and medication reminders  
- **3**: Emergency assistance
- **9**: AI voice assistant (records user speech)

### 3. Voice Recording
When users press 9, they can speak their concerns and MAMA-AI will:
- Record their voice
- Process the audio (future: convert to text)
- Provide appropriate AI responses

## Setup Instructions

### Step 1: Environment Configuration

Make sure your `.env` file has these voice settings:
```bash
# Voice Settings
BASE_URL=https://yourdomain.com  # Your public domain
VOICE_PHONE_NUMBER=+254700000000  # Your AT voice number
```

### Step 2: Africa's Talking Dashboard Setup

1. **Login** to your Africa's Talking dashboard
2. **Navigate** to Voice > Phone Numbers
3. **Select** your voice number
4. **Set Callback URL** to: `https://yourdomain.com/voice`
5. **Enable** Voice capabilities

### Step 3: Testing Locally

1. **Start the Flask app**:
   ```bash
   python app.py
   ```

2. **Run tests** (choose one):
   ```bash
   # Python test
   python test_voice.py
   
   # PowerShell test (Windows)
   .\test_voice.ps1
   ```

3. **Use ngrok** for public testing:
   ```bash
   ngrok http 5000
   # Copy the HTTPS URL to Africa's Talking callback
   ```

## API Endpoints

### POST /voice
Handles voice callbacks from Africa's Talking.

**Request Parameters:**
- `sessionId`: Unique session identifier
- `phoneNumber`: Caller's phone number
- `isActive`: Whether call is active (1/0)
- `dtmfDigits`: Touch-tone input from user
- `recordingUrl`: URL of voice recording (if any)
- `durationInSeconds`: Call duration

**Response:** TwiML-like XML for voice instructions

### POST /make_call
Initiates outbound calls (for reminders, etc.)

**Request Body:**
```json
{
  "phone_number": "+254700000000",
  "message": "Hello, this is a reminder..."
}
```

## Voice Flows

### 1. Incoming Call Flow
```
User calls → Welcome message → Menu options → User presses key → Specific action
```

### 2. Pregnancy Symptoms (Press 1)
```
User presses 1 → "Please describe your symptoms after the beep" → Record → "Thank you, our AI will analyze this"
```

### 3. Appointments (Press 2)
```
User presses 2 → Check database → Read upcoming appointments → Offer to set reminders
```

### 4. Emergency (Press 3)
```
User presses 3 → "This is for emergencies only" → Emergency checklist → Connect to health facility
```

### 5. AI Assistant (Press 9)
```
User presses 9 → "Speak your question" → Record → Process with AI → Respond with advice
```

## Testing Guide

### Local Testing
1. Start the app: `python app.py`
2. Run test script: `python test_voice.py`
3. Check console output for success/failure

### Live Testing with ngrok
1. Install ngrok: Download from ngrok.com
2. Start ngrok: `ngrok http 5000`
3. Copy HTTPS URL (e.g., `https://abc123.ngrok.io`)
4. Update Africa's Talking callback to: `https://abc123.ngrok.io/voice`
5. Call your Africa's Talking number

### Test Scenarios
1. **Basic Menu**: Call and listen to welcome message
2. **DTMF Navigation**: Press 1, 2, 3, 9 and verify responses
3. **Voice Recording**: Press 9, speak, verify recording URL is received
4. **Session Management**: Make multiple calls, verify sessions are tracked

## Troubleshooting

### Common Issues

1. **"Application not running"**
   - Solution: Start Flask app with `python app.py`
   - Check: `http://localhost:5000/health` returns 200

2. **"Callback not working"**
   - Solution: Use HTTPS URL (ngrok for testing)
   - Check: Africa's Talking dashboard has correct callback URL

3. **"No voice response"**
   - Solution: Check XML response format in logs
   - Verify: TwiML syntax is correct

4. **"Recording not received"**
   - Solution: Check `recordingUrl` parameter in callback
   - Verify: Africa's Talking voice settings allow recordings

### Debug Tips

1. **Check Logs**: Monitor Flask console for callback data
2. **Test Endpoints**: Use test scripts to verify functionality
3. **Verify Environment**: Ensure all `.env` variables are set
4. **Check AT Dashboard**: Verify callback URL and voice settings

## Next Steps

1. **Deploy to Production**: Use a cloud service (Heroku, AWS, etc.)
2. **Add Speech-to-Text**: Integrate Google/Azure Speech APIs
3. **Improve AI Responses**: Enhance the AI service for voice
4. **Add More Languages**: Support Kiswahili voice responses
5. **Analytics**: Track call metrics and user interactions

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Africa's Talking voice documentation
3. Test with the provided scripts
4. Verify your account has voice capabilities enabled

---

**Happy coding! 🎙️✨**
