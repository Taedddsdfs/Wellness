"""
The Wellness London Chatbot Backend API
Flask backend with SQLite database for booking management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import openai
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wellness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

db = SQLAlchemy(app)

# OpenAI configuration for AI responses
openai.api_key = os.getenv('OPENAI_API_KEY')

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    customer_name = db.Column(db.String(100))
    customer_email = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True)
    messages = db.Column(db.Text)  # JSON string of conversation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_email = db.Column(db.String(100))
    
class HealthAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))
    symptoms = db.Column(db.Text)
    category = db.Column(db.String(50))  # fatigue, weight, skin, hormonal, mental, nutrition
    severity = db.Column(db.Integer)  # 1-10 scale
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# API Routes

@app.route('/api/health-check', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Wellness London API'})

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages with AI-powered responses
    """
    try:
        data = request.json
        message = data.get('message')
        session_id = data.get('session_id')
        
        # Get AI response (simplified - you'd want more sophisticated logic)
        response = get_ai_response(message)
        
        # Log conversation
        logger.info(f"Chat - Session: {session_id}, Message: {message[:50]}...")
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/api/symptom-check', methods=['POST'])
def symptom_check():
    """
    Analyze symptoms and provide health recommendations
    """
    try:
        data = request.json
        symptoms = data.get('symptoms', [])
        category = data.get('category')
        
        # Analyze symptoms (simplified logic)
        recommendations = analyze_symptoms(symptoms, category)
        
        # Save assessment
        assessment = HealthAssessment(
            session_id=data.get('session_id'),
            symptoms=str(symptoms),
            category=category,
            recommendations=str(recommendations)
        )
        db.session.add(assessment)
        db.session.commit()
        
        return jsonify({
            'recommendations': recommendations,
            'severity': calculate_severity(symptoms),
            'should_see_doctor': should_see_doctor(symptoms)
        })
    except Exception as e:
        logger.error(f"Symptom check error: {str(e)}")
        return jsonify({'error': 'Failed to analyze symptoms'}), 500

@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    """
    Book an appointment and send confirmation email
    """
    try:
        data = request.json
        
        # Create booking
        booking = Booking(
            service=data.get('service'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d').date(),
            time=data.get('time'),
            customer_name=data.get('name'),
            customer_email=data.get('email'),
            customer_phone=data.get('phone'),
            notes=data.get('notes')
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Send confirmation email
        if booking.customer_email:
            send_confirmation_email(booking)
        
        logger.info(f"Booking created: {booking.id} - {booking.service}")
        
        return jsonify({
            'booking_id': booking.id,
            'status': 'confirmed',
            'message': 'Appointment booked successfully'
        })
    except Exception as e:
        logger.error(f"Booking error: {str(e)}")
        return jsonify({'error': 'Failed to book appointment'}), 500

@app.route('/api/services', methods=['GET'])
def get_services():
    """
    Get available services and pricing
    """
    services = [
        {
            'id': 'gp',
            'name': 'Private GP Consultation',
            'price': 'From £45',
            'duration': '15-30 minutes',
            'description': 'Same-day appointments available'
        },
        {
            'id': 'blood',
            'name': 'Blood Testing',
            'price': 'From £400',
            'duration': '15 minutes',
            'description': 'Same-day results'
        },
        {
            'id': 'iv',
            'name': 'IV Therapy',
            'price': 'From £295',
            'duration': '45 minutes',
            'description': 'Personalized vitamin infusions'
        },
        {
            'id': 'weight',
            'name': 'Weight Loss Program',
            'price': 'From £349',
            'duration': '3-6 months',
            'description': 'Medical weight management'
        },
        {
            'id': 'prp',
            'name': 'PRP Treatment',
            'price': 'From £475',
            'duration': '60 minutes',
            'description': 'Hair, skin & joint therapy'
        },
        {
            'id': 'facial',
            'name': 'Medical Facial',
            'price': 'Contact for pricing',
            'duration': '60-90 minutes',
            'description': 'Medical-grade treatments'
        }
    ]
    return jsonify(services)

@app.route('/api/available-slots', methods=['GET'])
def get_available_slots():
    """
    Get available appointment slots
    """
    date = request.args.get('date')
    service = request.args.get('service')
    
    # This would check against existing bookings in production
    slots = [
        '08:00', '09:00', '10:00', '11:00', 
        '14:00', '15:00', '16:00', '17:00', '18:00'
    ]
    
    return jsonify({'date': date, 'slots': slots})

# Helper Functions

def get_ai_response(message):
    """
    Get AI response for user message
    Uses OpenAI API or fallback to rule-based responses
    """
    try:
        if openai.api_key:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant for The Wellness London. Provide helpful, accurate medical information but always recommend seeing a doctor for serious concerns."},
                    {"role": "user", "content": message}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content
    except:
        pass
    
    # Fallback to rule-based responses
    message_lower = message.lower()
    
    if 'appointment' in message_lower or 'book' in message_lower:
        return "I can help you book an appointment. We offer GP consultations, blood testing, IV therapy, weight management programs, PRP treatments, and medical facials. Which service interests you?"
    elif 'price' in message_lower or 'cost' in message_lower:
        return "Our prices start from £45 for GP consultations, £400 for blood tests, £295 for IV therapy, £349 for weight programs, and £475 for PRP treatments."
    elif 'hours' in message_lower or 'open' in message_lower:
        return "We're open Monday-Friday 8am-8pm, Saturday 9am-5pm, and Sunday 10am-4pm."
    else:
        return "I'm here to help with your health needs. You can ask about our services, book appointments, or get health information. How can I assist you today?"

def analyze_symptoms(symptoms, category):
    """
    Analyze symptoms and provide recommendations
    """
    recommendations = []
    
    if category == 'fatigue':
        recommendations.append("Consider our comprehensive blood testing to check vitamin levels")
        recommendations.append("IV therapy can help boost energy levels")
    elif category == 'weight':
        recommendations.append("Our medical weight management program provides personalized support")
        recommendations.append("Book a GP consultation for a comprehensive assessment")
    elif category == 'skin':
        recommendations.append("Medical facials can address various skin concerns")
        recommendations.append("PRP treatments offer advanced skin rejuvenation")
    
    return recommendations

def calculate_severity(symptoms):
    """Calculate symptom severity on 1-10 scale"""
    # Simplified logic - would be more sophisticated in production
    return min(len(symptoms) * 2, 10)

def should_see_doctor(symptoms):
    """Determine if user should see a doctor immediately"""
    urgent_keywords = ['chest pain', 'difficulty breathing', 'severe', 'emergency']
    return any(keyword in str(symptoms).lower() for keyword in urgent_keywords)

def send_confirmation_email(booking):
    """
    Send appointment confirmation email
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = booking.customer_email
        msg['Subject'] = 'Appointment Confirmation - The Wellness London'
        
        body = f"""
        Dear {booking.customer_name},
        
        Your appointment has been confirmed:
        
        Service: {booking.service}
        Date: {booking.date.strftime('%B %d, %Y')}
        Time: {booking.time}
        
        Location: The Wellness London
        Please arrive 10 minutes early for check-in.
        
        If you need to reschedule, please call us at 07961 280835.
        
        Best regards,
        The Wellness London Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Confirmation email sent to {booking.customer_email}")
    except Exception as e:
        logger.error(f"Email error: {str(e)}")

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()
    logger.info("Database tables created")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
