# 📱 Testing MAMA-AI SMS with Africa's Talking Simulator

## 🚀 Step-by-Step Testing Guide

### Step 1: Access the Simulator
1. Open your web browser
2. Go to: **https://simulator.africastalking.com/**
3. Login with your Africa's Talking credentials:
   - Username: `sandbox`
   - Password: Your account password

### Step 2: Set Up SMS Testing
1. Once logged in, look for **"SMS"** section
2. Click on **"Send SMS"** or **"SMS Simulator"**
3. You should see options to simulate receiving SMS

### Step 3: Configure Your App URL
**IMPORTANT**: The simulator needs to know where to send webhook calls.

Your current app is running on: `http://127.0.0.1:5000`

But the simulator can't reach localhost, so you need to:

#### Option A: Use ngrok (Recommended)
1. Download ngrok from: https://ngrok.com/
2. Install and run: `ngrok http 5000`
3. Copy the public URL (like: `https://abc123.ngrok.io`)
4. Your SMS webhook URL becomes: `https://abc123.ngrok.io/sms`

#### Option B: Deploy temporarily to a service like Heroku/Railway

### Step 4: Configure Webhook in Africa's Talking
1. In your Africa's Talking dashboard
2. Go to **SMS → Settings → Callback URLs**
3. Set **SMS Callback URL** to: `https://your-ngrok-url.ngrok.io/sms`
4. Set **Delivery Report URL** to: `https://your-ngrok-url.ngrok.io/delivery-report`

### Step 5: Test SMS Messages
In the simulator, test these messages to shortcode **15629**:

#### Test Case 1: First Contact
```
From: +254712345678
To: 15629
Message: START
```
**Expected**: AI welcome message

#### Test Case 2: Health Question
```
From: +254712345678
To: 15629
Message: I'm 20 weeks pregnant and having morning sickness
```
**Expected**: AI health advice

#### Test Case 3: Help Request
```
From: +254712345678
To: 15629
Message: HELP
```
**Expected**: AI explanation of service

#### Test Case 4: Different User
```
From: +254787654321
To: 15629
Message: My baby is 3 months old and won't stop crying
```
**Expected**: AI parenting advice

#### Test Case 5: Unsubscribe
```
From: +254712345678
To: 15629
Message: STOP
```
**Expected**: AI goodbye message

## 🔧 Quick Setup with ngrok

### Download and Setup ngrok:
1. Go to https://ngrok.com/download
2. Download for Windows
3. Extract to a folder
4. Open PowerShell in that folder
5. Run: `./ngrok http 5000`

### You'll see output like:
```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000
```

### Use the HTTPS URL:
- Copy: `https://abc123.ngrok.io`
- Your SMS webhook: `https://abc123.ngrok.io/sms`

## 📊 What to Watch For

### In Your Flask App Console:
```
📱 Received SMS from +254712345678: START
✅ New user created: +254712345678
🤖 AI Response sent: Welcome to MAMA-AI...
```

### In ngrok Console (http://127.0.0.1:4040):
- You'll see incoming webhook requests
- Check if POST requests to `/sms` are successful

### In Africa's Talking Simulator:
- You should see SMS responses appear
- Check delivery status

## 🐛 Troubleshooting

### If no responses appear:
1. ✅ Check Flask app is running (`python app.py`)
2. ✅ Check ngrok is running and tunnel is active
3. ✅ Verify webhook URL is correct in Africa's Talking
4. ✅ Check Flask console for incoming requests
5. ✅ Check ngrok web interface for request logs

### Common Issues:
- **Webhook not configured**: SMS received but no processing
- **Wrong URL**: 404 errors in ngrok logs
- **App not running**: Connection refused errors
- **SSL issues**: Use HTTPS ngrok URL, not HTTP

## 🎯 Success Indicators

✅ **SMS Received**: Flask console shows "Received SMS from..."
✅ **User Created**: Console shows "New user created..."  
✅ **AI Processing**: Console shows AI response being generated
✅ **Response Sent**: Console shows "AI Response sent..."
✅ **No Hardcoded**: All responses should be unique and contextual

## 🔄 Alternative Testing Method

If simulator doesn't work, you can test the webhook directly:

```bash
# Test with curl (in PowerShell)
Invoke-RestMethod -Uri "http://127.0.0.1:5000/sms" -Method POST -Body @{
    from = "+254712345678"
    to = "15629"
    text = "Hello MAMA-AI, I need help"
    date = "2025-05-29 10:30:00"
}
```

This simulates an incoming SMS and should trigger AI response processing.

---

**Your SMS service is ready! The AI is working perfectly, you just need to make it accessible via ngrok for the simulator to reach it.** 🚀
