#!/usr/bin/env python3
"""
Production Configuration for MAMA-AI
This file contains optimized settings for production deployment
"""

import os
from datetime import datetime, timedelta
import africastalking
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Production Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(32))
    
    # Database Configuration - Use PostgreSQL in production
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///mama_ai.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
    app.config['SQLALCHEMY_POOL_RECYCLE'] = -1
    app.config['SQLALCHEMY_POOL_PRE_PING'] = True
    
    # Production settings
    app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/mama_ai.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('MAMA-AI startup')
    
    return app

app = create_app()

# Initialize extensions
from src.models import db, User, Pregnancy, Appointment, Reminder
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Africa's Talking
username = os.getenv('AFRICASTALKING_USERNAME')
api_key = os.getenv('AFRICASTALKING_API_KEY')
environment = os.getenv('AFRICASTALKING_ENVIRONMENT', 'sandbox')
shortcode = os.getenv('AFRICASTALKING_SHORTCODE')

# Initialize Africa's Talking with production settings
if username and api_key:
    try:
        africastalking.initialize(username, api_key)
        app.logger.info(f"✅ Africa's Talking initialized successfully!")
        app.logger.info(f"   Username: {username}")
        app.logger.info(f"   Environment: {environment}")
        app.logger.info(f"   Shortcode: {shortcode}")
    except Exception as e:
        app.logger.error(f"⚠️  Africa's Talking initialization failed: {str(e)}")
        raise
else:
    app.logger.error("❌ Missing Africa's Talking credentials")
    raise ValueError("Africa's Talking credentials not found")

# Initialize services
from src.services.ussd_service import USSDService
from src.services.sms_service import SMSService
from src.services.ai_service import AIService
from src.utils.language_utils import LanguageDetector

ussd_service = USSDService()
sms_service = SMSService()
ai_service = AIService()
language_detector = LanguageDetector()

# Production Health Check
@app.route('/health')
def health_check():
    """Comprehensive health check for production monitoring"""
    try:
        # Test database connection
        db.engine.execute("SELECT 1").scalar()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    # Test Africa's Talking
    at_status = "configured" if username and api_key else "not_configured"
    
    # Check service status
    services_status = {
        "ussd_service": "active" if ussd_service else "inactive",
        "sms_service": "active" if sms_service else "inactive", 
        "ai_service": "active" if ai_service else "inactive"
    }
    
    # Overall health
    is_healthy = db_status == "healthy" and at_status == "configured"
    
    return jsonify({
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": environment,
        "version": "1.0.0",
        "services": {
            "database": db_status,
            "africastalking": at_status,
            **services_status
        },
        "endpoints": {
            "ussd": "/ussd",
            "sms": "/sms", 
            "delivery_report": "/delivery-report",
            "chat": "/chat",
            "health": "/health"
        }
    }), 200 if is_healthy else 503

# Production USSD Handler
@app.route('/ussd', methods=['POST'])
def ussd_callback():
    """Production USSD webhook handler"""
    try:
        # Get USSD parameters
        session_id = request.form.get('sessionId')
        service_code = request.form.get('serviceCode')
        phone_number = request.form.get('phoneNumber')
        text = request.form.get('text', '')
        
        app.logger.info(f"USSD Request - Session: {session_id}, Phone: {phone_number}, Text: {text}")
        
        # Process USSD request
        response = ussd_service.handle_request(
            session_id=session_id,
            phone_number=phone_number,
            text=text,
            service_code=service_code
        )
        
        app.logger.info(f"USSD Response - Session: {session_id}, Response: {response[:100]}...")
        
        return response, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        app.logger.error(f"USSD Error: {str(e)}")
        return "END Sorry, there was an error processing your request. Please try again later.", 200

# Production SMS Handler
@app.route('/sms', methods=['POST'])
def sms_callback():
    """Production SMS webhook handler"""
    try:
        # Get SMS parameters
        from_number = request.form.get('from')
        to_number = request.form.get('to')
        text = request.form.get('text')
        date = request.form.get('date')
        message_id = request.form.get('id')
        
        app.logger.info(f"SMS Received - From: {from_number}, Text: {text[:50]}...")
        
        # Process SMS
        response = sms_service.handle_incoming_sms(
            from_number=from_number,
            to_number=to_number,
            text=text,
            received_at=date
        )
        
        app.logger.info(f"SMS Processed - Status: {response.get('status')}")
        
        return jsonify({"status": "success", "message": "SMS processed"}), 200
        
    except Exception as e:
        app.logger.error(f"SMS Error: {str(e)}")
        return jsonify({"status": "error", "message": "Processing failed"}), 500

# Production Delivery Report Handler
@app.route('/delivery-report', methods=['POST'])
def delivery_report():
    """Production delivery report handler"""
    try:
        message_id = request.form.get('id')
        status = request.form.get('status')
        phone_number = request.form.get('phoneNumber')
        
        app.logger.info(f"Delivery Report - ID: {message_id}, Status: {status}, Phone: {phone_number}")
        
        return jsonify({"status": "received"}), 200
        
    except Exception as e:
        app.logger.error(f"Delivery report error: {str(e)}")
        return jsonify({"status": "error"}), 500

# Root endpoint
@app.route('/')
def home():
    """API information endpoint"""
    return jsonify({
        "service": "MAMA-AI: AI-Powered Maternal Health Assistant",
        "status": "active",
        "version": "1.0.0",
        "environment": environment,
        "endpoints": {
            "ussd": "/ussd",
            "sms": "/sms",
            "delivery_report": "/delivery-report", 
            "health": "/health"
        },
        "description": "Supporting maternal health across Africa via SMS and USSD"
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f"Internal error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "An unexpected error occurred"}), 500

# Initialize database
@app.before_first_request
def create_tables():
    """Create database tables on first request"""
    try:
        db.create_all()
        app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Database initialization error: {str(e)}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
