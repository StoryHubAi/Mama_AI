import os
import logging
from datetime import datetime, timedelta
import africastalking
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from src.models import db, User, Pregnancy, Appointment, Reminder, MessageLog
from src.services.ussd_service import USSDService
from src.services.sms_service import SMSService
from src.services.voice_service import VoiceService
from src.services.ai_service import AIService
from src.utils.language_utils import LanguageDetector

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for frontend integration
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mama_ai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Production configuration
if os.getenv('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
else:
    app.config['DEBUG'] = True

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Africa's Talking with enhanced error handling
username = os.getenv('AFRICASTALKING_USERNAME')
api_key = os.getenv('AFRICASTALKING_API_KEY')
environment = os.getenv('AFRICASTALKING_ENVIRONMENT', 'sandbox')
shortcode = os.getenv('AFRICASTALKING_SHORTCODE', '985')

# Initialize Africa's Talking with proper credentials
if username and api_key and api_key != 'test_api_key_for_development':
    try:
        africastalking.initialize(username, api_key)
        logger.info(f"✅ Africa's Talking initialized successfully!")
        logger.info(f"   Username: {username}")
        logger.info(f"   Environment: {environment}")
        logger.info(f"   Shortcode: {shortcode}")
        at_initialized = True
    except Exception as e:
        logger.error(f"⚠️  Africa's Talking initialization failed: {str(e)}")
        logger.error("   Please check your credentials and try again")
        at_initialized = False
else:
    logger.warning("⚠️  Running in development mode without valid Africa's Talking credentials")
    at_initialized = False

# Initialize services
ussd_service = USSDService()
sms_service = SMSService()
voice_service = VoiceService()
ai_service = AIService()

# Create database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("✅ Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
language_detector = LanguageDetector()

@app.route('/')
def home():
    return jsonify({
        "message": "MAMA-AI: Your AI-Powered Maternal Health Assistant",
        "status": "active",
        "version": "1.0.0"
    })

@app.route('/ussd', methods=['POST'])
def ussd_callback():
    """Handle USSD requests from Africa's Talking"""
    try:
        # Get USSD parameters
        session_id = request.form.get('sessionId')
        service_code = request.form.get('serviceCode')
        phone_number = request.form.get('phoneNumber')
        text = request.form.get('text', '')
        
        # Log incoming USSD request
        logger.info(f"📞 USSD Request: SessionID={session_id}, Phone={phone_number}, Text='{text}'")
        
        # Process USSD request
        response = ussd_service.handle_request(
            session_id=session_id,
            phone_number=phone_number,
            text=text,
            service_code=service_code
        )
        
        logger.info(f"📤 USSD Response: {response[:50]}...")
        return response, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        logger.error(f"❌ USSD Error: {str(e)}")
        return "END Sorry, there was an error processing your request. Please try again.", 200

@app.route('/sms', methods=['POST'])
def sms_callback():
    """Handle incoming SMS from Africa's Talking with enhanced logging"""
    try:
        # Get SMS parameters
        from_number = request.form.get('from')
        to_number = request.form.get('to')
        text = request.form.get('text')
        date = request.form.get('date')
        
        # Enhanced logging for debugging
        logger.info(f"📨 Incoming SMS: From={from_number}, To={to_number}, Text='{text}'")
        
        # Validate required parameters
        if not from_number or not text:
            logger.error("❌ Missing required SMS parameters")
            return jsonify({"status": "error", "message": "Missing required parameters"}), 400
        
        # Process SMS
        response_data = sms_service.handle_incoming_sms(
            from_number=from_number,
            to_number=to_number,
            text=text,
            received_at=date
        )
        
        logger.info(f"📤 SMS Processing Result: {response_data}")
        
        return jsonify({
            "status": "success", 
            "message": "SMS processed successfully",
            "response_data": response_data,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        app.logger.error(f"SMS Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delivery-report', methods=['POST'])
def delivery_report():
    """Handle SMS delivery reports"""
    try:
        # Get delivery report parameters
        message_id = request.form.get('id')
        status = request.form.get('status')
        phone_number = request.form.get('phoneNumber')
        
        # Log delivery status
        app.logger.info(f"Delivery report - ID: {message_id}, Status: {status}, Phone: {phone_number}")
        
        return jsonify({"status": "received"}), 200
        
    except Exception as e:
        app.logger.error(f"Delivery report error: {str(e)}")
        return jsonify({"status": "error"}), 500

@app.route('/test-sms', methods=['POST'])
def test_sms():
    """Test SMS sending functionality"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        phone_number = data.get('phone_number', '').strip()
        message = data.get('message', 'Hello from MAMA-AI! 🤱 This is a test message.')
        
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400
        
        # Send test SMS
        result = sms_service.send_sms(phone_number, message)
        
        if result:
            return jsonify({
                "status": "success",
                "message": "SMS sent successfully",
                "phone_number": phone_number,
                "result": str(result)
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to send SMS"
            }), 500
            
    except Exception as e:
        app.logger.error(f"Test SMS Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500

@app.route('/test-sms-response', methods=['POST', 'GET'])
def test_sms_response():
    """Enhanced SMS response testing endpoint"""
    try:
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            from_number = data.get('from', '+254700000001')
            text = data.get('text', 'hi')
        else:
            from_number = request.args.get('from', '+254700000001')
            text = request.args.get('text', 'hi')
        
        # Clean phone number
        clean_phone = sms_service._clean_phone_number(from_number)
        
        # Get or create user
        user = User.query.filter_by(phone_number=clean_phone).first()
        if not user:
            user = User(
                phone_number=clean_phone,
                name="Test User",
                preferred_language="en",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
        
        # Generate AI response
        ai_response = sms_service._process_sms_content(text.lower(), user)
        
        # Log for debugging
        logger.info(f"🧪 Test SMS: '{text}' → '{ai_response[:50]}...'")
        
        return jsonify({
            "test_info": {
                "incoming_sms": text,
                "from_number": clean_phone,
                "user_id": user.id,
                "user_language": user.preferred_language,
                "user_name": user.name
            },
            "ai_response": ai_response,
            "response_length": len(ai_response) if ai_response else 0,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        })
        
    except Exception as e:
        logger.error(f"❌ Test SMS Error: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error",
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/test-dashboard')
def test_dashboard():
    """Interactive testing dashboard"""
    dashboard_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MAMA-AI Testing Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .test-form { display: flex; gap: 10px; margin: 10px 0; align-items: center; }
            input[type="text"] { flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
            button { padding: 8px 15px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #2980b9; }
            .response { margin: 10px 0; padding: 10px; background: #ecf0f1; border-radius: 4px; white-space: pre-wrap; }
            .quick-tests { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
            .quick-test { padding: 10px; background: #e8f4fd; border-radius: 4px; cursor: pointer; text-align: center; }
            .quick-test:hover { background: #d1ecf1; }
            .status { text-align: center; margin: 10px 0; }
            .logs { height: 300px; overflow-y: auto; background: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 4px; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤱 MAMA-AI Testing Dashboard</h1>
            
            <div class="section">
                <h3>📱 SMS Chat Tester</h3>
                <div class="test-form">
                    <input type="text" id="phoneInput" placeholder="Phone Number (+254700000001)" value="+254700000001">
                    <input type="text" id="messageInput" placeholder="Type your message here..." value="hi">
                    <button onclick="testSMS()">Send Test SMS</button>
                </div>
                <div id="response" class="response" style="display:none;"></div>
            </div>
            
            <div class="section">
                <h3>🚀 Quick Tests</h3>
                <div class="quick-tests">
                    <div class="quick-test" onclick="quickTest('hi')">👋 Greeting</div>
                    <div class="quick-test" onclick="quickTest('help')">❓ Help Command</div>
                    <div class="quick-test" onclick="quickTest('I have back pain')">🏥 Symptom Report</div>
                    <div class="quick-test" onclick="quickTest('emergency')">🚨 Emergency</div>
                    <div class="quick-test" onclick="quickTest('when is baby due')">👶 Baby Questions</div>
                    <div class="quick-test" onclick="quickTest('appointment')">📅 Appointment</div>
                    <div class="quick-test" onclick="quickTest('reminder')">⏰ Reminder</div>
                    <div class="quick-test" onclick="quickTest('stop')">⛔ Unsubscribe</div>
                </div>
            </div>
            
            <div class="section">
                <h3>📊 System Status</h3>
                <div id="systemStatus" class="status">Loading...</div>
                <button onclick="checkHealth()">Refresh Status</button>
            </div>
            
            <div class="section">
                <h3>📋 Activity Logs</h3>
                <div id="logs" class="logs">Logs will appear here...</div>
            </div>
        </div>

        <script>
            let logCount = 0;
            
            async function testSMS() {
                const phone = document.getElementById('phoneInput').value;
                const message = document.getElementById('messageInput').value;
                const responseDiv = document.getElementById('response');
                
                if (!message.trim()) {
                    alert('Please enter a message');
                    return;
                }
                
                responseDiv.style.display = 'block';
                responseDiv.innerHTML = 'Testing...';
                
                addLog(`📤 Testing: "${message}" from ${phone}`);
                
                try {
                    const response = await fetch('/test-sms-response', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ from: phone, text: message })
                    });
                    
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        responseDiv.innerHTML = `
                            <strong>✅ AI Response:</strong>
                            ${data.ai_response}
                            
                            <small>
                            📱 From: ${data.test_info.from_number}
                            👤 User: ${data.test_info.user_name}
                            🌐 Language: ${data.test_info.user_language}
                            📏 Length: ${data.response_length} chars
                            ⏰ Time: ${new Date(data.timestamp).toLocaleTimeString()}
                            </small>
                        `;
                        addLog(`📥 Response: "${data.ai_response.substring(0, 50)}..."`);
                    } else {
                        responseDiv.innerHTML = `❌ Error: ${data.error}`;
                        addLog(`❌ Error: ${data.error}`);
                    }
                } catch (error) {
                    responseDiv.innerHTML = `❌ Network Error: ${error.message}`;
                    addLog(`❌ Network Error: ${error.message}`);
                }
            }
            
            function quickTest(message) {
                document.getElementById('messageInput').value = message;
                testSMS();
            }
            
            async function checkHealth() {
                const statusDiv = document.getElementById('systemStatus');
                statusDiv.innerHTML = 'Checking...';
                
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    
                    statusDiv.innerHTML = `
                        <strong>Status:</strong> ${data.status} <br>
                        <strong>Database:</strong> ${data.services.database} <br>
                        <strong>Africa's Talking:</strong> ${data.services.africastalking} <br>
                        <strong>Environment:</strong> ${data.services.environment} <br>
                        <strong>Username:</strong> ${data.services.username} <br>
                        <strong>Shortcode:</strong> ${data.services.shortcode}
                    `;
                    addLog(`💚 System Status: ${data.status}`);
                } catch (error) {
                    statusDiv.innerHTML = `❌ Health Check Failed: ${error.message}`;
                    addLog(`❌ Health Check Failed: ${error.message}`);
                }
            }
            
            function addLog(message) {
                const logsDiv = document.getElementById('logs');
                const timestamp = new Date().toLocaleTimeString();
                logsDiv.innerHTML += `[${timestamp}] ${message}\\n`;
                logsDiv.scrollTop = logsDiv.scrollHeight;
                
                logCount++;
                if (logCount > 50) {
                    const lines = logsDiv.innerHTML.split('\\n');
                    logsDiv.innerHTML = lines.slice(-40).join('\\n');
                    logCount = 40;
                }
            }
            
            // Auto-load system status
            window.onload = function() {
                checkHealth();
                addLog('🚀 MAMA-AI Testing Dashboard Loaded');
                
                // Enable Enter key for message input
                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        testSMS();
                    }
                });
            };
        </script>
    </body>
    </html>
    '''
    return dashboard_html

@app.route('/send-reminders', methods=['POST'])
def send_reminders():
    """Endpoint to manually trigger reminder sending (for testing)"""
    try:
        sent_count = sms_service.send_scheduled_reminders()
        return jsonify({
            "status": "success",
            "reminders_sent": sent_count
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/chat', methods=['POST'])
def chat_with_ai():
    """Chat endpoint for AI conversations"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        message = data.get('message', '').strip()
        phone_number = data.get('phone_number', '').strip()
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400
        
        # Clean phone number
        clean_phone = ussd_service._clean_phone_number(phone_number)
        
        # Get or create user
        user = ussd_service._get_or_create_user(clean_phone)
        
        # Get conversation history if provided
        conversation_history = data.get('conversation_history', [])
        
        # Process message with AI
        response = ai_service.chat_with_ai(message, user, conversation_history)
        
        return jsonify({
            "status": "success",
            "response": response,
            "user": {
                "phone_number": user.phone_number,
                "name": user.name,
                "preferred_language": user.preferred_language
            },
            "timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        app.logger.error(f"Chat Error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Sorry, I encountered an error processing your message. Please try again."
        }), 500

@app.route('/chat-interface')
def chat_interface():
    """Simple web chat interface"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MAMA-AI Chat Interface</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            .chat-container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            .header {
                background: white;
                border-radius: 15px 15px 0 0;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .header h1 {
                margin: 0;
                color: #667eea;
                font-size: 2em;
            }
            
            .header p {
                margin: 10px 0 0 0;
                color: #666;
                font-size: 1.1em;
            }
            
            .chat-messages {
                flex: 1;
                background: white;
                padding: 20px;
                overflow-y: auto;
                max-height: 500px;
            }
            
            .message {
                margin-bottom: 15px;
                padding: 12px 18px;
                border-radius: 20px;
                max-width: 80%;
                word-wrap: break-word;
                white-space: pre-wrap;
            }
            
            .user-message {
                background: #667eea;
                color: white;
                margin-left: auto;
                border-bottom-right-radius: 5px;
            }
            
            .ai-message {
                background: #f1f3f4;
                color: #333;
                margin-right: auto;
                border-bottom-left-radius: 5px;
            }
            
            .input-container {
                background: white;
                border-radius: 0 0 15px 15px;
                padding: 20px;
                display: flex;
                gap: 10px;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            }
            
            .phone-input {
                width: 150px;
                padding: 12px;
                border: 2px solid #e1e5e9;
                border-radius: 25px;
                font-size: 14px;
                outline: none;
            }
            
            .phone-input:focus {
                border-color: #667eea;
            }
            
            .message-input {
                flex: 1;
                padding: 12px 20px;
                border: 2px solid #e1e5e9;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                resize: none;
            }
            
            .message-input:focus {
                border-color: #667eea;
            }
            
            .send-button {
                padding: 12px 25px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: background 0.3s;
            }
            
            .send-button:hover {
                background: #5a6fd8;
            }
            
            .send-button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            .typing-indicator {
                display: none;
                align-items: center;
                margin: 10px 0;
                color: #666;
                font-style: italic;
            }
            
            .typing-dots {
                display: inline-block;
                margin-left: 10px;
            }
            
            .typing-dots span {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #667eea;
                margin: 0 2px;
                animation: typing 1.4s infinite both;
            }
            
            .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
            .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
            
            @keyframes typing {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-10px); }
            }
            
            .intro-message {
                background: #e8f4fd;
                border: 1px solid #b8daff;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                color: #0c5460;
            }
            
            .examples {
                margin-top: 10px;
                font-size: 0.9em;
            }
            
            .examples strong {
                display: block;
                margin-bottom: 5px;
            }
            
            @media (max-width: 600px) {
                .chat-container {
                    padding: 10px;
                }
                
                .input-container {
                    flex-direction: column;
                }
                
                .phone-input {
                    width: 100%;
                }
                
                .message {
                    max-width: 95%;
                }
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="header">
                <h1>🤱 MAMA-AI</h1>
                <p>AI-Powered Maternal Health Assistant</p>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="intro-message">
                    <strong>Welcome to MAMA-AI! 👋</strong>
                    <p>I'm your AI-powered maternal health assistant. I can help you with:</p>
                    <div class="examples">
                        <strong>Try asking:</strong>
                        • "I'm experiencing morning sickness, what should I do?"<br>
                        • "How often should I feel baby movements?"<br>
                        • "What foods should I avoid during pregnancy?"<br>
                        • "I have a severe headache and blurred vision"<br>
                        • "When is my next appointment?"
                    </div>
                    <p><strong>Note:</strong> For medical emergencies, always call 911 immediately.</p>
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                MAMA-AI is typing
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
            
            <div class="input-container">
                <input 
                    type="tel" 
                    class="phone-input" 
                    id="phoneInput" 
                    placeholder="+254700000000"
                    value="+254700000000"
                >
                <textarea 
                    class="message-input" 
                    id="messageInput" 
                    placeholder="Type your message here... (English or Kiswahili)"
                    rows="1"
                ></textarea>
                <button class="send-button" id="sendButton" onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            let conversationHistory = [];
            
            function addMessage(content, isUser = false) {
                const messagesContainer = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
                messageDiv.textContent = content;
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            function showTypingIndicator() {
                document.getElementById('typingIndicator').style.display = 'flex';
                document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
            }
            
            function hideTypingIndicator() {
                document.getElementById('typingIndicator').style.display = 'none';
            }
            
            async function sendMessage() {
                const messageInput = document.getElementById('messageInput');
                const phoneInput = document.getElementById('phoneInput');
                const sendButton = document.getElementById('sendButton');
                
                const message = messageInput.value.trim();
                const phoneNumber = phoneInput.value.trim();
                
                if (!message || !phoneNumber) {
                    alert('Please enter both phone number and message');
                    return;
                }
                
                // Add user message to chat
                addMessage(message, true);
                conversationHistory.push({type: 'user', message: message, timestamp: new Date().toISOString()});
                
                // Clear input and disable button
                messageInput.value = '';
                sendButton.disabled = true;
                showTypingIndicator();
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            phone_number: phoneNumber,
                            conversation_history: conversationHistory
                        })
                    });
                    
                    const data = await response.json();
                    hideTypingIndicator();
                    
                    if (data.status === 'success') {
                        addMessage(data.response, false);
                        conversationHistory.push({type: 'ai', message: data.response, timestamp: new Date().toISOString()});
                    } else {
                        addMessage('Sorry, I encountered an error. Please try again.', false);
                    }
                } catch (error) {
                    hideTypingIndicator();
                    addMessage('Sorry, I couldn\\'t connect to the server. Please check your internet connection and try again.', false);
                    console.error('Error:', error);
                } finally {
                    sendButton.disabled = false;
                    messageInput.focus();
                }
            }
            
            // Handle Enter key press
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            // Auto-resize textarea
            document.getElementById('messageInput').addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
            
            // Focus on message input when page loads
            document.getElementById('messageInput').focus();
        </script>
    </body>
    </html>
    '''

@app.route('/sandbox')
def sandbox_interface():
    """Africa's Talking Sandbox Testing Interface"""
    try:
        with open('templates/sandbox.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Sandbox interface not found"}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint with comprehensive system status"""
    try:
        # Test database connection using SQLAlchemy 2.0 syntax
        from sqlalchemy import text, inspect
        result = db.session.execute(text("SELECT 1")).scalar()
        
        # Get database stats
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        # Count records in main tables
        user_count = User.query.count()
        pregnancy_count = Pregnancy.query.count()
        appointment_count = Appointment.query.count()
        
        db_status = {
            "status": "connected",
            "tables": len(tables),
            "users": user_count,
            "pregnancies": pregnancy_count,
            "appointments": appointment_count
        }
    except Exception as e:
        db_status = {
            "status": "disconnected",
            "error": str(e)
        }
    
    # Check Africa's Talking status
    at_status = {
        "status": "configured" if at_initialized else "not_configured",
        "username": username,
        "environment": environment,
        "shortcode": shortcode
    }
    
    # System information
    system_info = {
        "python_version": os.sys.version.split()[0],
        "flask_env": os.getenv('FLASK_ENV', 'development'),
        "debug_mode": app.config.get('DEBUG', False)
    }
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": db_status,
            "africastalking": at_status,
            "system": system_info
        },
        "endpoints": {
            "home": "/",
            "health": "/health",
            "sms_webhook": "/sms",
            "ussd_webhook": "/ussd",
            "test_sms": "/test-sms-response",
            "test_dashboard": "/test-dashboard",
            "chat_interface": "/chat-interface",
            "sandbox": "/sandbox",
            "delivery_reports": "/delivery-report"
        }
    })

@app.route('/stats', methods=['GET'])
def system_stats():
    """Get detailed system statistics"""
    try:
        # Database statistics
        stats = {
            "users": {
                "total": User.query.count(),
                "active": User.query.filter_by(is_active=True).count(),
                "inactive": User.query.filter_by(is_active=False).count()
            },
            "pregnancies": {
                "total": Pregnancy.query.count(),
                "active": Pregnancy.query.filter_by(is_active=True).count() if hasattr(Pregnancy, 'is_active') else 0
            },
            "appointments": {
                "total": Appointment.query.count(),
                "upcoming": Appointment.query.filter(
                    Appointment.appointment_date > datetime.utcnow(),
                    Appointment.status == 'scheduled'
                ).count() if hasattr(Appointment, 'appointment_date') else 0
            },
            "messages": {
                "total": MessageLog.query.count() if 'MessageLog' in globals() else 0
            }
        }
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

# =============================================================================
# VOICE API ENDPOINTS
# =============================================================================

@app.route('/voice', methods=['POST'])
def voice_callback():
    """Handle incoming voice calls from Africa's Talking"""
    try:
        # Get voice call parameters
        session_id = request.form.get('sessionId')
        phone_number = request.form.get('phoneNumber')
        is_active = request.form.get('isActive')
        
        app.logger.info(f"Voice call - Session: {session_id}, Phone: {phone_number}, Active: {is_active}")
        
        # Handle the incoming call
        response = voice_service.handle_incoming_call(
            session_id=session_id,
            phone_number=phone_number,
            is_active=is_active
        )
        
        return response, 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        app.logger.error(f"Voice callback error: {str(e)}")
        return voice_service._create_error_response(), 200, {'Content-Type': 'application/xml'}

@app.route('/voice/dtmf', methods=['POST'])
def voice_dtmf():
    """Handle DTMF input during voice calls"""
    try:
        session_id = request.form.get('sessionId')
        phone_number = request.form.get('phoneNumber')
        dtmf_digits = request.form.get('dtmfDigits')
        
        app.logger.info(f"DTMF input - Session: {session_id}, Phone: {phone_number}, Digits: {dtmf_digits}")
        
        # Process DTMF input
        response = voice_service.handle_dtmf_input(
            session_id=session_id,
            phone_number=phone_number,
            dtmf_digits=dtmf_digits
        )
        
        return response, 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        app.logger.error(f"DTMF error: {str(e)}")
        return voice_service._create_error_response(), 200, {'Content-Type': 'application/xml'}

@app.route('/voice/pregnancy', methods=['POST'])
def voice_pregnancy():
    """Handle pregnancy tracking voice input"""
    try:
        session_id = request.form.get('sessionId')
        phone_number = request.form.get('phoneNumber')
        dtmf_digits = request.form.get('dtmfDigits')
        
        # Get user
        clean_phone = voice_service._clean_phone_number(phone_number)
        user = voice_service._get_or_create_user(clean_phone)
        
        # Process pregnancy-specific input
        response = voice_service._process_pregnancy_input(dtmf_digits, user, session_id)
        
        return response, 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        app.logger.error(f"Voice pregnancy error: {str(e)}")
        return voice_service._create_error_response(), 200, {'Content-Type': 'application/xml'}

@app.route('/voice/health', methods=['POST'])
def voice_health():
    """Handle health check voice input"""
    try:
        session_id = request.form.get('sessionId')
        phone_number = request.form.get('phoneNumber')
        dtmf_digits = request.form.get('dtmfDigits')
        
        # Get user
        clean_phone = voice_service._clean_phone_number(phone_number)
        user = voice_service._get_or_create_user(clean_phone)
        
        # Process health-specific input
        response = voice_service._process_health_input(dtmf_digits, user, session_id)
        
        return response, 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        app.logger.error(f"Voice health error: {str(e)}")
        return voice_service._create_error_response(), 200, {'Content-Type': 'application/xml'}

@app.route('/voice/appointments', methods=['POST'])
def voice_appointments():
    """Handle appointments voice input"""
    try:
        session_id = request.form.get('sessionId')
        phone_number = request.form.get('phoneNumber')
        dtmf_digits = request.form.get('dtmfDigits')
        
        # Get user
        clean_phone = voice_service._clean_phone_number(phone_number)
        user = voice_service._get_or_create_user(clean_phone)
        
        # Process appointments-specific input
        response = voice_service._process_appointments_input(dtmf_digits, user, session_id)
        
        return response, 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        app.logger.error(f"Voice appointments error: {str(e)}")
        return voice_service._create_error_response(), 200, {'Content-Type': 'application/xml'}

@app.route('/voice/emergency', methods=['POST'])
def voice_emergency():
    """Handle emergency voice input with immediate response"""
    try:
        session_id = request.form.get('sessionId')
        phone_number = request.form.get('phoneNumber')
        dtmf_digits = request.form.get('dtmfDigits')
        
        # Get user
        clean_phone = voice_service._clean_phone_number(phone_number)
        user = voice_service._get_or_create_user(clean_phone)
        
        # Process emergency input with high priority
        response = voice_service._process_emergency_input(dtmf_digits, user, session_id)
        
        return response, 200, {'Content-Type': 'application/xml'}
        
    except Exception as e:
        app.logger.error(f"Voice emergency error: {str(e)}")
        return voice_service._create_error_response(), 200, {'Content-Type': 'application/xml'}

@app.route('/voice/make-call', methods=['POST'])
def make_outbound_call():
    """Endpoint to make outbound voice calls (for reminders, emergencies)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        phone_number = data.get('phone_number', '').strip()
        message = data.get('message', '').strip()
        voice_type = data.get('voice_type', 'woman')
        
        if not phone_number or not message:
            return jsonify({"error": "Phone number and message are required"}), 400
        
        # Make the outbound call
        result = voice_service.make_outbound_call(phone_number, message, voice_type)
        
        if result:
            return jsonify({
                "status": "success",
                "message": "Call initiated successfully",
                "result": str(result)
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to initiate call"
            }), 500
            
    except Exception as e:
        app.logger.error(f"Outbound call error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500

# =============================================================================
# END VOICE API ENDPOINTS
# =============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
