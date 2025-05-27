import os
from datetime import datetime, timedelta
import africastalking
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from src.models import db, User, Pregnancy, Appointment, Reminder
from src.services.ussd_service import USSDService
from src.services.sms_service import SMSService
from src.services.ai_service import AIService
from src.utils.language_utils import LanguageDetector

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mama_ai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Initialize Africa's Talking
username = os.getenv('AFRICASTALKING_USERNAME')
api_key = os.getenv('AFRICASTALKING_API_KEY')
environment = os.getenv('AFRICASTALKING_ENVIRONMENT', 'sandbox')

# Initialize Africa's Talking with proper credentials
if username and api_key and api_key != 'test_api_key_for_development':
    try:
        africastalking.initialize(username, api_key)
        print(f"✅ Africa's Talking initialized successfully!")
        print(f"   Username: {username}")
        print(f"   Environment: {environment}")
        print(f"   Shortcode: {os.getenv('AFRICASTALKING_SHORTCODE', 'Not set')}")
    except Exception as e:
        print(f"⚠️  Africa's Talking initialization failed: {str(e)}")
        print("   Please check your credentials and try again")
else:
    print("⚠️  Running in development mode without valid Africa's Talking credentials")

# Initialize services
ussd_service = USSDService()
sms_service = SMSService()
ai_service = AIService()
language_detector = LanguageDetector()

@app.route('/')
def home():
    return jsonify({
        "message": "MAMA-AI: AI-Powered Maternal Health Assistant",
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
        
        # Process USSD request
        response = ussd_service.handle_request(
            session_id=session_id,
            phone_number=phone_number,
            text=text,
            service_code=service_code
        )
        
        return response, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        app.logger.error(f"USSD Error: {str(e)}")
        return "END Sorry, there was an error processing your request. Please try again.", 200

@app.route('/sms', methods=['POST'])
def sms_callback():
    """Handle incoming SMS from Africa's Talking"""
    try:
        # Get SMS parameters
        from_number = request.form.get('from')
        to_number = request.form.get('to')
        text = request.form.get('text')
        date = request.form.get('date')
        
        # Process SMS
        response = sms_service.handle_incoming_sms(
            from_number=from_number,
            to_number=to_number,
            text=text,
            received_at=date
        )
        
        return jsonify({"status": "success", "message": "SMS processed"}), 200
        
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
    """Health check endpoint"""
    try:
        db_status = "connected" if db.engine.execute("SELECT 1").scalar() else "disconnected"
    except:
        db_status = "disconnected"
    
    at_status = "configured" if username and api_key and api_key != 'test_api_key_for_development' else "not_configured"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "africastalking": at_status,
            "environment": environment,
            "username": username,
            "shortcode": os.getenv('AFRICASTALKING_SHORTCODE', 'Not set')
        },        "endpoints": {
            "chat": "/chat",
            "sms_callback": "/sms", 
            "ussd_callback": "/ussd",
            "delivery_report": "/delivery-report",
            "test_sms": "/test-sms",
            "chat_interface": "/chat-interface",
            "sandbox": "/sandbox"
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
