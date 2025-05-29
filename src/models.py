from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    preferred_language = db.Column(db.String(5), default='en')
    location = db.Column(db.String(100))
    emergency_contact = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pregnancies = db.relationship('Pregnancy', backref='user', lazy=True)
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    reminders = db.relationship('Reminder', backref='user', lazy=True)
    conversations = db.relationship('Conversation', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.phone_number}>'

class Pregnancy(db.Model):
    __tablename__ = 'pregnancies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    weeks_pregnant = db.Column(db.Integer)
    is_high_risk = db.Column(db.Boolean, default=False)
    health_conditions = db.Column(db.Text)
    current_symptoms = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pregnancy {self.id} - User {self.user_id}>'

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    appointment_type = db.Column(db.String(50))  # checkup, vaccination, scan, etc.
    location = db.Column(db.String(200))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.appointment_type}>'

class Reminder(db.Model):
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reminder_type = db.Column(db.String(50))  # medication, appointment, checkup
    message = db.Column(db.Text, nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    frequency = db.Column(db.String(20))  # daily, weekly, monthly, once
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reminder {self.id} - {self.reminder_type}>'

class MessageLog(db.Model):
    __tablename__ = 'message_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    message_type = db.Column(db.String(10))  # SMS, USSD
    direction = db.Column(db.String(10))  # incoming, outgoing
    content = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MessageLog {self.id} - {self.message_type}>'

class EmergencyAlert(db.Model):
    __tablename__ = 'emergency_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(50))  # severe_bleeding, severe_pain, etc.
    symptoms_reported = db.Column(db.Text)
    severity_score = db.Column(db.Integer)  # 1-10
    action_taken = db.Column(db.String(100))
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmergencyAlert {self.id} - {self.alert_type}>'

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100))  # For grouping related messages
    channel = db.Column(db.String(10))  # SMS, USSD
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    intent_detected = db.Column(db.String(50))  # symptoms, appointment, emergency, etc.
    confidence_score = db.Column(db.Float)
    language_detected = db.Column(db.String(5))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Conversation {self.id} - User {self.user_id}>'
