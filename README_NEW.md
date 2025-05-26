# MAMA-AI: AI-Powered Maternal Health Assistant

🏆 **Africa's Talking Hackathon 2025 – 2G Meets AI Solutions**

## Overview
MAMA-AI is an AI-driven maternal health assistant running over USSD, SMS, and web chat, delivering personalized pregnancy support, reminders, and emergency triage for mothers in low-connectivity regions.

## Features
- 🍼 **Personalized pregnancy tracking** - Monitor symptoms, baby movements, and pregnancy progress
- 📱 **Multilingual USSD/SMS interactions** - Support for English and Kiswahili
- 💬 **AI-powered chat interface** - Natural language conversations about pregnancy health
- 🚑 **Emergency detection & escalation** - Automatic detection of serious symptoms with immediate guidance
- 💊 **Appointment & medication reminders** - Automated SMS reminders for important healthcare visits
- 🔌 **Offline-first design** - Works with basic phones using Africa's Talking APIs
- 🌍 **Cultural sensitivity** - Designed for African maternal health contexts

## Tech Stack
- **Backend**: Python 3.x with Flask
- **Database**: SQLAlchemy (SQLite for development, PostgreSQL for production)
- **APIs**: Africa's Talking SDK (USSD, SMS)
- **AI/NLP**: Custom multilingual processing for English and Kiswahili
- **Frontend**: Responsive web chat interface
- **Background Tasks**: Celery with Redis
- **Deployment**: Docker ready with CI/CD support

## Quick Start

### 1. Setup Environment
```bash
# Clone repository
git clone https://github.com/yourname/mama-ai-hackathon.git
cd MAMA-AI

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your Africa's Talking credentials
```

### 2. Initialize Database
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 3. Run Application
```bash
python app.py
```

### 4. Access Interfaces
- **Web Chat Interface**: http://localhost:5000/chat-interface
- **API Health Check**: http://localhost:5000/health
- **USSD Callback**: http://localhost:5000/ussd (for Africa's Talking)
- **SMS Callback**: http://localhost:5000/sms (for Africa's Talking)

## Key Features

### 💬 AI Chat Interface
The web chat interface allows users to have natural conversations with MAMA-AI in both English and Kiswahili. Simply visit `/chat-interface` to start chatting about:
- Pregnancy symptoms and concerns
- Baby development and movement
- Nutrition and health advice
- Emergency situations
- Appointment scheduling

### 📱 USSD Integration
Dial your configured shortcode to access:
- Pregnancy tracking menus
- Health check options
- Appointment management
- Emergency assistance
- Language settings

### 📨 SMS Commands
Text any of these commands:
- `HELP` - Get help and available commands
- `SYMPTOMS` - Report pregnancy symptoms
- `APPOINTMENT` - Check upcoming appointments
- `EMERGENCY` - Get emergency guidance
- `STOP/START` - Unsubscribe/subscribe

## Africa's Talking Setup

1. **Get API Credentials**: Sign up at [Africa's Talking](https://africastalking.com)
2. **Configure USSD**: Set callback URL to `https://yourdomain.com/ussd`
3. **Configure SMS**: Set callback URL to `https://yourdomain.com/sms`
4. **Add Credentials**: Update your `.env` file with your credentials

---

**MAMA-AI - Empowering African Mothers with AI** 🤱✨
