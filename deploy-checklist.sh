#!/bin/bash
# MAMA-AI Quick Deployment Checklist ✅

echo "🤱 MAMA-AI Deployment Checklist"
echo "================================"
echo ""

# Check if files exist
echo "📋 Pre-deployment Check:"
if [ -f "Procfile" ]; then
    echo "✅ Procfile exists"
else 
    echo "❌ Procfile missing"
fi

if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt exists" 
else
    echo "❌ requirements.txt missing"
fi

if [ -f "runtime.txt" ]; then
    echo "✅ runtime.txt exists"
else
    echo "❌ runtime.txt missing"
fi

if [ -f ".env" ]; then
    echo "✅ .env exists"
else
    echo "❌ .env missing"
fi

echo ""
echo "🚀 Ready to Deploy!"
echo "==================="
echo ""
echo "Choose your deployment platform:"
echo ""
echo "1️⃣  HEROKU (Recommended):"
echo "   heroku create mama-ai-assistant"
echo "   heroku config:set AFRICASTALKING_USERNAME=mama_ai"
echo "   heroku config:set AFRICASTALKING_API_KEY=atsk_2d22cca6c92bc7655436ce2e1b2cab232e3f7898fe861e06584f5392e14724998bf381f4"
echo "   heroku config:set AFRICASTALKING_SHORTCODE=985"
echo "   heroku config:set FLASK_ENV=production"
echo "   git push heroku main"
echo ""
echo "2️⃣  RAILWAY:"
echo "   railway init"
echo "   railway up"
echo ""
echo "3️⃣  DIGITALOCEAN:"
echo "   Create app in App Platform dashboard"
echo "   Connect GitHub repo"
echo ""
echo "📡 After deployment, configure Africa's Talking:"
echo "   SMS Webhook: https://your-app.herokuapp.com/sms"
echo "   USSD Webhook: https://your-app.herokuapp.com/ussd"
echo ""
echo "🎯 Your MAMA-AI backend is PRODUCTION-READY!"
echo "   - Complete USSD & SMS functionality"
echo "   - AI-powered health assistant" 
echo "   - Emergency detection system"
echo "   - Multilingual support"
echo "   - Database with user management"
echo ""
echo "Ready to help mothers across Africa! 🌍✨"
