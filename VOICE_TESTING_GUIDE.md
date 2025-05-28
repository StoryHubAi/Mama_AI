# 🎙️ Testing MAMA-AI Voice with Africa's Talking Simulator

## Step-by-Step Guide to Test Voice Integration

### Step 1: Setup Your Environment

First, make sure your `.env` file has the correct values:

```bash
# Copy .env.example to .env
cp .env.example .env
```

Then edit `.env` with your Africa's Talking credentials:
```bash
AFRICASTALKING_USERNAME=sandbox  # Keep as 'sandbox' for testing
AFRICASTALKING_API_KEY=your_actual_api_key_here
AFRICASTALKING_SHORTCODE=your_shortcode_here
BASE_URL=https://your-ngrok-url.ngrok.io  # We'll set this up next
VOICE_PHONE_NUMBER=+254727230675  # Your AT voice number
```

### Step 2: Make Your App Publicly Accessible

Since Africa's Talking needs to reach your localhost, we'll use ngrok:

#### Option A: Using ngrok (Recommended for Testing)
1. Download ngrok from https://ngrok.com/download
2. Extract and place ngrok.exe in your project folder
3. Start your Flask app first:
   ```powershell
   python app.py
   ```
4. In a new terminal, run ngrok:
   ```powershell
   .\ngrok.exe http 5000
   ```
5. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
6. Update your `.env` file:
   ```bash
   BASE_URL=https://abc123.ngrok.io
   ```

#### Option B: Using Railway/Heroku (For Persistent Testing)
If you want a more permanent solution, deploy to a cloud service.

### Step 3: Configure Africa's Talking Dashboard

1. **Login** to https://account.africastalking.com
2. **Go to Voice** > Voice Numbers
3. **Select your voice number** or get a new one
4. **Set Callback URL**: `https://your-ngrok-url.ngrok.io/voice`
5. **Enable DTMF** (touch-tone support)
6. **Save settings**

### Step 4: Test Voice Integration

#### Method 1: Using Africa's Talking Voice Simulator
1. In your AT dashboard, go to **Voice** > **Voice Simulator**
2. Enter your voice number
3. Click **Make Call**
4. You should hear the voice menu!

#### Method 2: Call Your Number Directly
1. Use your phone to call your AT voice number
2. Listen to the voice menu
3. Press 1, 2, 3, 4, or 9 to test different options

### Step 5: Expected Voice Flow

When you call, you should hear:
```
🔊 "Welcome to MAMA-AI, your maternal health assistant."
🔊 "Press 1 for pregnancy tracking"
🔊 "Press 2 for health check"  
🔊 "Press 3 for appointments"
🔊 "Press 4 for emergency"
🔊 "Press 9 to repeat menu"
```

Then when you press a number:
- **Press 1**: Pregnancy tracking menu
- **Press 2**: Health check options  
- **Press 3**: Appointment management
- **Press 4**: Emergency assistance
- **Press 9**: Repeat the main menu

## Troubleshooting

### Issue: "Call Failed" or No Response
**Solution**: 
- Check ngrok is running and URL is correct
- Verify callback URL in AT dashboard
- Check Flask app logs for errors

### Issue: Can't Hear Voice
**Solution**:
- Check your phone volume
- Try the AT Voice Simulator first
- Verify voice number is correct

### Issue: DTMF Not Working
**Solution**:
- Ensure DTMF is enabled in AT dashboard
- Check that `GetDigits` XML is properly formatted
- Verify callback URLs are accessible

## Testing Checklist

- [ ] Flask app running on localhost:5000
- [ ] ngrok exposing app publicly
- [ ] AT dashboard configured with correct callback URL
- [ ] Voice number working
- [ ] Can make test call and hear voice menu
- [ ] DTMF input (pressing numbers) works
- [ ] Each menu option responds correctly
- [ ] Database logging is working

## Debug Tips

1. **Check Flask Logs**: Watch the terminal for incoming requests
2. **Test Endpoints**: Use our test script: `python test_voice.py`
3. **Verify XML**: Check that responses are valid XML format
4. **AT Logs**: Check AT dashboard for call logs and errors

You're all set to test your voice integration! 🎉
