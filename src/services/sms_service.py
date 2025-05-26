import os
import africastalking
from datetime import datetime, timedelta
from src.models import db, User, Reminder, MessageLog, Appointment
from src.utils.language_utils import get_translation
from src.services.ai_service import AIService

class SMSService:
    def __init__(self):
        self.sms = africastalking.SMS
        self.ai_service = AIService()
    
    def send_sms(self, phone_number, message, sender_id=None):
        """Send SMS using Africa's Talking"""
        try:
            # Clean phone number
            clean_phone = self._clean_phone_number(phone_number)
            
            # Send SMS
            response = self.sms.send(
                message=message,
                recipients=[clean_phone],
                sender_id=sender_id
            )
            
            # Log the SMS
            self._log_message(clean_phone, "SMS", "outgoing", message)
            
            return response
            
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            return None
    
    def handle_incoming_sms(self, from_number, to_number, text, received_at):
        """Handle incoming SMS messages"""
        try:
            # Clean phone number
            clean_phone = self._clean_phone_number(from_number)
            
            # Log incoming SMS
            self._log_message(clean_phone, "SMS", "incoming", text)
            
            # Get or create user
            user = self._get_or_create_user(clean_phone)
            
            # Process the SMS based on content
            response = self._process_sms_content(text.strip().lower(), user)
            
            if response:
                # Send response SMS
                self.send_sms(clean_phone, response)
            
            return {"status": "processed", "response_sent": bool(response)}
            
        except Exception as e:
            print(f"Error handling incoming SMS: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _process_sms_content(self, text, user):
        """Process SMS content and generate appropriate response"""
        lang = user.preferred_language
        
        # Check for specific keywords
        if any(keyword in text for keyword in ['help', 'msaada', 'emergency', 'dharura']):
            return self._handle_help_request(user)
        
        elif any(keyword in text for keyword in ['stop', 'acha', 'unsubscribe']):
            return self._handle_stop_request(user)
        
        elif any(keyword in text for keyword in ['start', 'anza', 'subscribe']):
            return self._handle_start_request(user)
        
        elif any(keyword in text for keyword in ['appointment', 'miadi', 'clinic']):
            return self._handle_appointment_request(user)
        
        elif any(keyword in text for keyword in ['symptoms', 'dalili', 'pain', 'bleeding']):
            return self._handle_symptoms_report(text, user)
        
        elif any(keyword in text for keyword in ['reminder', 'ukumbusho', 'medicine', 'dawa']):
            return self._handle_reminder_request(user)
        
        else:
            # Use AI to understand and respond to the message
            return self.ai_service.process_free_text_query(text, user)
    
    def _handle_help_request(self, user):
        """Handle help requests"""
        lang = user.preferred_language
        
        help_msg = get_translation(lang, "sms_help",
            "MAMA-AI Help 📱\n\n"
            "SMS Commands:\n"
            "• HELP - This help message\n"
            "• SYMPTOMS - Report symptoms\n"
            "• APPOINTMENT - Check appointments\n"
            "• REMINDER - Set medication reminder\n"
            "• EMERGENCY - Get emergency help\n"
            "• STOP - Unsubscribe\n\n"
            "USSD: Dial *123# for full menu\n\n"
            "Emergency: Call 911"
        )
        
        return help_msg
    
    def _handle_stop_request(self, user):
        """Handle unsubscribe requests"""
        lang = user.preferred_language
        
        # Deactivate user
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return get_translation(lang, "unsubscribed",
            "You have been unsubscribed from MAMA-AI messages. "
            "SMS START to reactivate. For emergencies, always call 911."
        )
    
    def _handle_start_request(self, user):
        """Handle subscription requests"""
        lang = user.preferred_language
        
        # Reactivate user
        user.is_active = True
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        welcome_msg = get_translation(lang, "welcome_back",
            "Welcome back to MAMA-AI! 🤱\n\n"
            "Your maternal health assistant is now active.\n\n"
            "Dial *123# for the full menu or SMS HELP for commands.\n\n"
            "We're here to support you through your pregnancy journey!"
        )
        
        return welcome_msg
    
    def _handle_appointment_request(self, user):
        """Handle appointment-related requests"""
        lang = user.preferred_language
        
        # Get next appointment
        next_appointment = Appointment.query.filter_by(
            user_id=user.id,
            status='scheduled'
        ).filter(
            Appointment.appointment_date > datetime.utcnow()
        ).order_by(Appointment.appointment_date).first()
        
        if next_appointment:
            date_str = next_appointment.appointment_date.strftime('%Y-%m-%d %H:%M')
            msg = get_translation(lang, "next_appointment",
                f"Your next appointment:\n"
                f"📅 {date_str}\n"
                f"🏥 {next_appointment.appointment_type}\n"
                f"📍 {next_appointment.location or 'Location TBD'}\n\n"
                f"We'll send you a reminder 24 hours before."
            )
        else:
            msg = get_translation(lang, "no_appointments",
                "You have no scheduled appointments. "
                "Contact your healthcare provider to schedule your next visit."
            )
        
        return msg
    
    def _handle_symptoms_report(self, text, user):
        """Handle symptoms reporting"""
        lang = user.preferred_language
        
        # Use AI to analyze symptoms
        analysis = self.ai_service.analyze_symptoms(text, user)
        
        # Update user's pregnancy record with symptoms
        self._update_pregnancy_symptoms(user, text)
        
        return analysis
    
    def _handle_reminder_request(self, user):
        """Handle reminder requests"""
        lang = user.preferred_language
        
        reminder_msg = get_translation(lang, "reminder_info",
            "Medication Reminders 💊\n\n"
            "To set up reminders:\n"
            "1. Dial *123# → Appointments\n"
            "2. Visit your healthcare provider\n"
            "3. We'll automatically set reminders\n\n"
            "For immediate medication questions, "
            "consult your healthcare provider."
        )
        
        return reminder_msg
    
    def send_scheduled_reminders(self):
        """Send scheduled reminders (called by background task)"""
        try:
            # Get reminders that should be sent now
            current_time = datetime.utcnow()
            due_reminders = Reminder.query.filter(
                Reminder.scheduled_time <= current_time,
                Reminder.sent == False
            ).all()
            
            sent_count = 0
            
            for reminder in due_reminders:
                user = User.query.get(reminder.user_id)
                if user and user.is_active:
                    # Send the reminder
                    response = self.send_sms(user.phone_number, reminder.message)
                    
                    if response:
                        # Mark as sent
                        reminder.sent = True
                        reminder.sent_at = datetime.utcnow()
                        sent_count += 1
                
                # Handle recurring reminders
                if reminder.frequency != 'once':
                    self._schedule_next_reminder(reminder)
            
            db.session.commit()
            return sent_count
            
        except Exception as e:
            print(f"Error sending scheduled reminders: {str(e)}")
            return 0
    
    def send_appointment_reminders(self):
        """Send appointment reminders 24 hours before"""
        try:
            # Get appointments in the next 24-25 hours that haven't been reminded
            tomorrow = datetime.utcnow() + timedelta(hours=24)
            day_after = datetime.utcnow() + timedelta(hours=25)
            
            upcoming_appointments = Appointment.query.filter(
                Appointment.appointment_date.between(tomorrow, day_after),
                Appointment.reminder_sent == False,
                Appointment.status == 'scheduled'
            ).all()
            
            sent_count = 0
            
            for appointment in upcoming_appointments:
                user = User.query.get(appointment.user_id)
                if user and user.is_active:
                    lang = user.preferred_language
                    
                    date_str = appointment.appointment_date.strftime('%Y-%m-%d at %H:%M')
                    reminder_msg = get_translation(lang, "appointment_reminder",
                        f"📅 APPOINTMENT REMINDER\n\n"
                        f"You have an appointment tomorrow:\n"
                        f"🕒 {date_str}\n"
                        f"🏥 {appointment.appointment_type}\n"
                        f"📍 {appointment.location or 'Contact clinic for location'}\n\n"
                        f"Please arrive 15 minutes early. "
                        f"Bring your pregnancy book and any questions."
                    )
                    
                    response = self.send_sms(user.phone_number, reminder_msg)
                    
                    if response:
                        appointment.reminder_sent = True
                        sent_count += 1
            
            db.session.commit()
            return sent_count
            
        except Exception as e:
            print(f"Error sending appointment reminders: {str(e)}")
            return 0
    
    def _schedule_next_reminder(self, reminder):
        """Schedule the next occurrence of a recurring reminder"""
        if reminder.frequency == 'daily':
            next_time = reminder.scheduled_time + timedelta(days=1)
        elif reminder.frequency == 'weekly':
            next_time = reminder.scheduled_time + timedelta(weeks=1)
        elif reminder.frequency == 'monthly':
            next_time = reminder.scheduled_time + timedelta(days=30)
        else:
            return  # One-time reminder
        
        # Create new reminder
        new_reminder = Reminder(
            user_id=reminder.user_id,
            reminder_type=reminder.reminder_type,
            message=reminder.message,
            scheduled_time=next_time,
            frequency=reminder.frequency
        )
        
        db.session.add(new_reminder)
    
    def _get_or_create_user(self, phone_number):
        """Get existing user or create new one"""
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            user = User(
                phone_number=phone_number,
                preferred_language='en',
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
        return user
    
    def _update_pregnancy_symptoms(self, user, symptoms):
        """Update pregnancy symptoms"""
        from src.models import Pregnancy
        pregnancy = Pregnancy.query.filter_by(
            user_id=user.id, 
            is_active=True
        ).first()
        
        if pregnancy:
            pregnancy.current_symptoms = symptoms
            pregnancy.updated_at = datetime.utcnow()
            db.session.commit()
    
    def _clean_phone_number(self, phone_number):
        """Clean and standardize phone number"""
        clean = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        if not clean.startswith('+'):
            if clean.startswith('0'):
                clean = '+254' + clean[1:]
            elif clean.startswith('254'):
                clean = '+' + clean
            else:
                clean = '+254' + clean
        
        return clean
    
    def _log_message(self, phone_number, msg_type, direction, content):
        """Log SMS message"""
        log = MessageLog(
            phone_number=phone_number,
            message_type=msg_type,
            direction=direction,
            content=content
        )
        db.session.add(log)
        db.session.commit()
