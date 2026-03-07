# MAMA-AI: AI-Powered Maternal Health Assistant
Africa’s Talking Hackathon 2025 – 2G Meets AI Solutions

## Overview
MAMA-AI is an AI-driven maternal health assistant running over USSD and SMS, delivering personalized pregnancy support, reminders, and emergency triage for mothers in low-connectivity regions.

## Features
- Personalized pregnancy tracking
- Multilingual (English & Kiswahili) USSD/SMS interactions
- Emergency detection & escalation
- Appointment & medication reminders
- Offline-first design using Africa’s Talking APIs

## Tech Stack
- Python 3.x
- Flask or FastAPI (for backend)
- Africa’s Talking SDK (for USSD, SMS)
- NLP libraries (for multilingual understanding)
- Docker (for containerization)
- GitHub Actions / Travis CI (for CI/CD)

## Setup
```bash
git clone https://github.com/yourname/mama-ai-hackathon.git
cd mama-ai-hackathon
pip install -r requirements.txt
python src/app.py
