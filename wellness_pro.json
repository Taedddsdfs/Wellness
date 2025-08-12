/**
 * The Wellness London - Professional AI Health Assistant
 * Enhanced with user management, compliance, analytics, and emergency features
 */

// Global variables
let recognition;
let isActive = false;
let isMuted = false;
let currentTranscriptBlock = null;
let speechSynth = window.speechSynthesis;
let currentSpeaker = null;
let callStartTime = null;
let callTimer = null;
let conversationLog = [];
let sessionId = generateSessionId();
let selectedService = null;
let selectedSymptoms = [];
let currentUser = null;
let assessmentData = {};

// Backend API configuration
const API_URL = 'http://localhost:5000/api';

// Emergency keywords that trigger alerts
const EMERGENCY_KEYWORDS = [
    'chest pain', 'heart attack', 'stroke', 'can\'t breathe', 'difficulty breathing', 
    'severe bleeding', 'unconscious', 'suicide', 'overdose', 'allergic reaction',
    'choking', 'severe pain', 'emergency', 'urgent', 'help me', 'dying'
];

// Analytics tracking
let analytics = {
    sessionStart: Date.now(),
    messageCount: 0,
    bookingAttempts: 0,
    emergencyTriggered: false,
    symptoms: [],
    userSatisfaction: null,
    conversationDuration: 0
};

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Error logging function
function logError(error, context = '') {
    const timestamp = new Date().toISOString();
    const errorInfo = {
        timestamp: timestamp,
        context: context,
        message: error.message || error,
        stack: error.stack || '',
        userAgent: navigator.userAgent,
        url: window.location.href,
        sessionId: sessionId,
        userId: currentUser?.id || 'guest'
    };
    
    console.error(`[${timestamp}] ${context}:`, error);
    
    // Store errors in localStorage
    try {
        const errors = JSON.parse(localStorage.getItem('wellnessErrors') || '[]');
        errors.push(errorInfo);
        if (errors.length > 50) errors.shift();
        localStorage.setItem('wellnessErrors', JSON.stringify(errors));
    } catch (storageError) {
        console.error('Failed to store error:', storageError);
    }
    
    // Send to analytics
    trackEvent('error', { context: context, message: error.message || error });
}

// Analytics tracking
function trackEvent(eventName, data = {}) {
    const event = {
        timestamp: new Date().toISOString(),
        sessionId: sessionId,
        userId: currentUser?.id || 'guest',
        eventName: eventName,
        data: data,
        userAgent: navigator.userAgent
    };
    
    // Store locally
    const events = JSON.parse(localStorage.getItem('wellnessAnalytics') || '[]');
    events.push(event);
    if (events.length > 1000) events.shift();
    localStorage.setItem('wellnessAnalytics', JSON.stringify(events));
    
    // Send to backend if available
    if (typeof fetch !== 'undefined') {
        fetch(`${API_URL}/analytics`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(event)
        }).catch(err => console.log('Analytics offline'));
    }
}

// Emergency detection
function checkForEmergency(text) {
    const lowerText = text.toLowerCase();
    const hasEmergencyKeyword = EMERGENCY_KEYWORDS.some(keyword => 
        lowerText.includes(keyword)
    );
    
    if (hasEmergencyKeyword && !analytics.emergencyTriggered) {
        analytics.emergencyTriggered = true;
        showEmergencyBanner();
        trackEvent('emergency_detected', { text: text });
        
        // Auto-respond with emergency guidance
        setTimeout(() => {
            const emergencyResponse = "I've detected this might be a medical emergency. For immediate help, please call 999. I'm also showing emergency options at the top of your screen.";
            addLiveTranscript(emergencyResponse, 'Wellness AI');
            speakResponse(emergencyResponse);
        }, 500);
        
        return true;
    }
    return false;
}

// Emergency functions
function showEmergencyBanner() {
    document.getElementById('emergencyBanner').classList.add('active');
}

function hideEmergency() {
    document.getElementById('emergencyBanner').classList.remove('active');
}

function call999() {
    // In a real app, this would initiate a call
    window.open('tel:999', '_self');
    trackEvent('emergency_call_999');
}

// Authentication functions
function showAuth() {
    document.getElementById('authModal').classList.add('active');
    trackEvent('auth_modal_opened');
}

function hideAuth() {
    document.getElementById('authModal').classList.remove('active');
}

function switchTab(tab) {
    const tabs = document.querySelectorAll('.auth-tab');
    const forms = document.querySelectorAll('.auth-form');
    
    tabs.forEach(t => t.classList.remove('active'));
    forms.forEach(f => f.style.display = 'none');
    
    document.querySelector(`[onclick="switchTab('${tab}')"]`).classList.add('active');
    document.getElementById(tab + 'Form').style.display = 'flex';
}

function startAsGuest() {
    currentUser = { id: 'guest', name: 'Guest User', type: 'guest' };
    initiateCall();
    trackEvent('started_as_guest');
}

// User registration/login handlers
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        // Simulate login - in real app, call backend
        currentUser = {
            id: 'user_' + Date.now(),
            name: email.split('@')[0],
            email: email,
            type: 'registered'
        };
        
        document.getElementById('userInfo').textContent = currentUser.name;
        hideAuth();
        initiateCall();
        trackEvent('user_login', { email: email });
    } catch (error) {
        logError(error, 'Login failed');
        alert('Login failed. Please try again.');
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const phone = document.getElementById('registerPhone').value;
    const password = document.getElementById('registerPassword').value;
    const gdprConsent = document.getElementById('gdprConsent').checked;
    const marketingConsent = document.getElementById('marketingConsent').checked;
    
    if (!gdprConsent) {
        alert('Please accept the Terms of Service and Privacy Policy to continue.');
        return;
    }
    
    try {
        // Simulate registration - in real app, call backend
        currentUser = {
            id: 'user_' + Date.now(),
            name: name,
            email: email,
            phone: phone,
            type: 'registered',
            gdprConsent: gdprConsent,
            marketingConsent: marketingConsent,
            registeredAt: new Date().toISOString()
        };
        
        // Store user data (encrypted in real app)
        localStorage.setItem('wellnessUser', JSON.stringify(currentUser));
        
        document.getElementById('userInfo').textContent = currentUser.name;
        hideAuth();
        initiateCall();
        trackEvent('user_registration', { email: email, marketingConsent: marketingConsent });
    } catch (error) {
        logError(error, 'Registration failed');
        alert('Registration failed. Please try again.');
    }
});

// Health Assessment functions
function showAssessment() {
    const panel = document.getElementById('assessmentPanel');
    panel.classList.toggle('active');
    if (panel.classList.contains('active')) {
        trackEvent('assessment_opened');
    }
}

function selectSymptom(symptom) {
    const btn = event.target;
    btn.classList.toggle('selected');
    
    if (btn.classList.contains('selected')) {
        selectedSymptoms.push(symptom);
    } else {
        selectedSymptoms = selectedSymptoms.filter(s => s !== symptom);
    }
    
    trackEvent('symptom_selected', { symptom: symptom, total: selectedSymptoms.length });
}

function updateSeverity() {
    const value = document.getElementById('severitySlider').value;
    document.getElementById('severityValue').textContent = value;
    assessmentData.severity = parseInt(value);
}

async function submitAssessment() {
    if (selectedSymptoms.length === 0) {
        alert('Please select at least one symptom or concern.');
        return;
    }
    
    assessmentData.symptoms = selectedSymptoms;
    assessmentData.severity = assessmentData.severity || 5;
    assessmentData.timestamp = new Date().toISOString();
    
    try {
        const response = await fetch(`${API_URL}/symptom-check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symptoms: selectedSymptoms,
                severity: assessmentData.severity,
                session_id: sessionId
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            showAssessmentResults(data);
        } else {
            throw new Error('Assessment API failed');
        }
    } catch (error) {
        logError(error, 'Assessment submission failed');
        showLocalAssessmentResults();
    }
    
    trackEvent('assessment_submitted', assessmentData);
}

function showAssessmentResults(data) {
    let recommendations = "Based on your assessment:\n\n";
    
    if (data.recommendations) {
        recommendations += data.recommendations.join('\n• ') + '\n\n';
    }
    
    if (data.should_see_doctor || assessmentData.severity >= 7) {
        recommendations += "⚠️ I recommend booking a consultation with one of our doctors.";
        showDoctorAlert();
    }
    
    addLiveTranscript(recommendations, 'Wellness AI');
    document.getElementById('assessmentPanel').classList.remove('active');
}

function showLocalAssessmentResults() {
    let recommendations = "Based on your selected symptoms:\n\n";
    
    selectedSymptoms.forEach(symptom => {
        switch(symptom) {
            case 'fatigue':
                recommendations += "• Consider our comprehensive blood testing\n• IV therapy may help boost energy\n";
                break;
            case 'weight':
                recommendations += "• Our medical weight management program provides support\n• Book a GP consultation for assessment\n";
                break;
            case 'skin':
                recommendations += "• Medical facials can address skin concerns\n• PRP treatments offer advanced rejuvenation\n";
                break;
            default:
                recommendations += `• Book a consultation to discuss your ${symptom} concerns\n`;
        }
    });
    
    if (assessmentData.severity >= 7) {
        recommendations += "\n⚠️ Given the severity, I recommend speaking with a doctor soon.";
        showDoctorAlert();
    }
    
    addLiveTranscript(recommendations, 'Wellness AI');
    document.getElementById('assessmentPanel').classList.remove('active');
}

function showDoctorAlert() {
    document.getElementById('doctorAlert').classList.add('active');
    setTimeout(() => {
        document.getElementById('doctorAlert').classList.remove('active');
    }, 10000); // Hide after 10 seconds
}

function bookHumanDoctor() {
    // Pre-select human doctor consultation
    selectedService = 'doctor';
    showBooking();
    
    // Pre-fill the form
    setTimeout(() => {
        const doctorOption = document.querySelector('[onclick*="doctor"]');
        if (doctorOption) {
            selectService('doctor', doctorOption);
        }
    }, 100);
    
    trackEvent('human_doctor_requested');
}

// Update call timer
function updateCallTimer() {
    if (!callStartTime) return;
    const elapsed = Math.floor((Date.now() - callStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('callTimer').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    analytics.conversationDuration = elapsed;
}

// Service selection
function selectService(service, element) {
    selectedService = service;
    document.querySelectorAll('.service-item').forEach(item => {
        item.classList.remove('selected');
    });
    element.classList.add('selected');
    updateBookingButton();
    trackEvent('service_selected', { service: service });
}

// Update booking button
function updateBookingButton() {
    const btn = document.getElementById('confirmBtn');
    const name = document.getElementById('bookingName').value;
    const email = document.getElementById('bookingEmail').value;
    const phone = document.getElementById('bookingPhone').value;
    const date = document.getElementById('bookingDate').value;
    const time = document.getElementById('bookingTime').value;
    
    if (selectedService && name && email && phone && date && time) {
        btn.disabled = false;
        btn.textContent = 'Confirm Booking';
    } else {
        btn.disabled = true;
        btn.textContent = 'Complete all fields to book';
    }
}

// Add event listeners to booking form fields
document.addEventListener('DOMContentLoaded', () => {
    const fields = ['bookingName', 'bookingEmail', 'bookingPhone', 'bookingDate', 'bookingTime'];
    fields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', updateBookingButton);
            field.addEventListener('change', updateBookingButton);
        }
    });
});

// Booking confirmation with full data collection
async function confirmBooking() {
    const name = document.getElementById('bookingName').value;
    const email = document.getElementById('bookingEmail').value;
    const phone = document.getElementById('bookingPhone').value;
    const date = document.getElementById('bookingDate').value;
    const time = document.getElementById('bookingTime').value;
    const notes = document.getElementById('bookingNotes').value;
    const reminderConsent = document.getElementById('reminderConsent').checked;
    
    if (!selectedService || !name || !email || !phone || !date || !time) {
        alert('Please complete all required fields.');
        return;
    }
    
    const btn = document.getElementById('confirmBtn');
    btn.textContent = 'Booking...';
    btn.disabled = true;
    
    const services = {
        'gp': 'Private GP Consultation',
        'blood': 'Blood Testing',
        'iv': 'IV Therapy',
        'weight': 'Weight Loss Program',
        'prp': 'PRP Treatment',
        'facial': 'Medical Facial',
        'doctor': 'Human Doctor Consultation'
    };
    
    const bookingData = {
        service: services[selectedService],
        serviceId: selectedService,
        name: name,
        email: email,
        phone: phone,
        date: date,
        time: time,
        notes: notes,
        reminderConsent: reminderConsent,
        sessionId: sessionId,
        userId: currentUser?.id || 'guest',
        assessmentData: selectedSymptoms.length > 0 ? assessmentData : null,
        timestamp: new Date().toISOString()
    };
    
    try {
        const response = await fetch(`${API_URL}/book-appointment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bookingData)
        });
        
        if (response.ok) {
            const data = await response.json();
            showBookingSuccess(bookingData, data.booking_id);
            trackEvent('booking_confirmed', { ...bookingData, booking_id: data.booking_id });
        } else {
            throw new Error('Booking API failed');
        }
    } catch (error) {
        logError(error, 'Booking API failed');
        
        // Fallback to local storage
        const bookings = JSON.parse(localStorage.getItem('wellnessBookings') || '[]');
        bookings.push(bookingData);
        localStorage.setItem('wellnessBookings', JSON.stringify(bookings));
        
        showBookingSuccess(bookingData, 'LOCAL_' + Date.now());
        trackEvent('booking_confirmed_local', bookingData);
    }
    
    analytics.bookingAttempts++;
}

function showBookingSuccess(bookingData, bookingId) {
    const dateObj = new Date(bookingData.date);
    const dateStr = dateObj.toLocaleDateString('en-GB', { 
        weekday: 'long', 
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    
    document.getElementById('bookingView').style.display = 'none';
    document.getElementById('bookingSuccess').classList.add('active');
    document.getElementById('bookingDetails').innerHTML = `
        <strong>${bookingData.service}</strong><br>
        ${dateStr} at ${bookingData.time}<br>
        <small>Booking ID: ${bookingId}</small>
    `;
    
    // Schedule reminder if consented
    if (bookingData.reminderConsent) {
        scheduleReminder(bookingData);
    }
    
    setTimeout(() => {
        hideBooking();
        setTimeout(resetBookingForm, 500);
    }, 3000);
}

function scheduleReminder(bookingData) {
    // In a real app, this would schedule server-side reminders
    const reminderDate = new Date(bookingData.date + 'T' + bookingData.time);
    reminderDate.setDate(reminderDate.getDate() - 1); // Day before
    
    if (reminderDate > new Date()) {
        const reminders = JSON.parse(localStorage.getItem('appointmentReminders') || '[]');
        reminders.push({
            id: Date.now(),
            appointmentDate: bookingData.date,
            appointmentTime: bookingData.time,
            service: bookingData.service,
            reminderDate: reminderDate.toISOString(),
            email: bookingData.email,
            phone: bookingData.phone
        });
        localStorage.setItem('appointmentReminders', JSON.stringify(reminders));
    }
}

function resetBookingForm() {
    document.getElementById('bookingView').style.display = 'block';
    document.getElementById('bookingSuccess').classList.remove('active');
    selectedService = null;
    document.getElementById('bookingForm').reset();
    document.querySelectorAll('.service-item').forEach(item => {
        item.classList.remove('selected');
    });
    updateBookingButton();
}

// Chat export functions
function exportChat() {
    document.getElementById('exportModal').classList.add('active');
    trackEvent('export_requested');
}

function hideExport() {
    document.getElementById('exportModal').classList.remove('active');
}

function exportAsPDF() {
    // Simple PDF generation - in real app, use proper PDF library
    const transcript = conversationLog.map(msg => 
        `${msg.speaker}: ${msg.text}`
    ).join('\n\n');
    
    const content = `
The Wellness London - Chat Transcript
Session: ${sessionId}
Date: ${new Date().toLocaleDateString()}
User: ${currentUser?.name || 'Guest'}

${transcript}

---
This transcript is for medical reference only.
For emergencies, call 999.
The Wellness London - info@thewellnesslondon.com
    `;
    
    downloadTextFile('wellness-chat-transcript.txt', content);
    trackEvent('export_pdf');
    hideExport();
}

function exportAsText() {
    const transcript = conversationLog.map(msg => 
        `[${new Date().toLocaleTimeString()}] ${msg.speaker}: ${msg.text}`
    ).join('\n\n');
    
    downloadTextFile('wellness-chat.txt', transcript);
    trackEvent('export_text');
    hideExport();
}

function emailTranscript() {
    const transcript = conversationLog.map(msg => 
        `${msg.speaker}: ${msg.text}`
    ).join('\\n\\n');
    
    const subject = 'The Wellness London - Chat Transcript';
    const body = `Here is your chat transcript from The Wellness London:\\n\\n${transcript}`;
    
    const email = currentUser?.email || prompt('Enter your email address:');
    if (email) {
        // In real app, send via backend API
        window.open(`mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`);
        trackEvent('export_email', { email: email });
    }
    hideExport();
}

function downloadTextFile(filename, content) {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Speech recognition setup
function setupSpeech() {
    try {
        if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
            logError('Speech recognition not supported', 'setupSpeech');
            document.getElementById('statusText').textContent = 'Type your questions below';
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-GB';

        recognition.onstart = () => {
            console.log('Recognition started');
            document.getElementById('statusText').textContent = 'Listening';
        };

        recognition.onresult = (event) => {
            let finalText = '';
            let interimText = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalText += transcript + ' ';
                } else {
                    interimText += transcript;
                }
            }

            if (finalText || interimText) {
                addLiveTranscript(finalText || interimText, 'you', !finalText);
                
                if (finalText) {
                    conversationLog.push({ speaker: 'you', text: finalText.trim() });
                    processInput(finalText.trim());
                }
            }
        };

        recognition.onerror = (event) => {
            logError(event.error, 'Speech recognition error');
            document.getElementById('statusText').textContent = 'Click mic to retry';
        };

        recognition.onend = () => {
            if (isActive && !isMuted) {
                setTimeout(() => recognition.start(), 100);
            }
        };
    } catch (error) {
        logError(error, 'setupSpeech');
    }
}

// Process input with emergency detection and backend API
async function processInput(text) {
    analytics.messageCount++;
    
    // Check for emergency first
    if (checkForEmergency(text)) {
        return;
    }
    
    const lower = text.toLowerCase();
    currentSpeaker = null;
    
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                session_id: sessionId,
                user_id: currentUser?.id || 'guest',
                symptoms: selectedSymptoms,
                assessment_data: assessmentData
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            hideTypingIndicator();
            
            addLiveTranscript(data.response, 'Wellness AI');
            conversationLog.push({ speaker: 'Wellness AI', text: data.response });
            
            if (speechSynth && !isMuted) {
                speakResponse(data.response);
            }
            
            trackEvent('ai_response', { input: text, response: data.response });
        } else {
            throw new Error('API response not ok');
        }
    } catch (error) {
        logError(error, 'API chat failed, using local processing');
        processInputLocally(text);
    }
}

// Local fallback processing
function processInputLocally(text) {
    const lower = text.toLowerCase();
    
    setTimeout(() => {
        hideTypingIndicator();
        let response = '';

        // Enhanced local responses
        if (lower.includes('doctor') || lower.includes('human')) {
            response = "I can connect you with one of our qualified doctors for a £60 video consultation. They can provide personalized medical advice and prescriptions if needed. Would you like to book this?";
            showDoctorAlert();
        } else if (lower.includes('gp') || lower.includes('consultation')) {
            response = "We offer private GP consultations starting from £45. You can get same-day appointments with our experienced doctors. Would you like to book a consultation?";
        } else if (lower.includes('blood') || lower.includes('test')) {
            response = "Our comprehensive blood testing starts from £400 with same-day results. We test for various health markers including vitamins, hormones, and metabolic panels. Would you like to schedule a blood test?";
        } else if (lower.includes('symptoms') || lower.includes('assessment')) {
            response = "I can help assess your symptoms. Click the 'Assessment' button at the top to complete a quick health questionnaire, or tell me about your specific concerns.";
        } else if (lower.includes('book') || lower.includes('appointment')) {
            response = "I can help you book an appointment. Click the calendar button below, or tell me which service interests you and I'll guide you through the booking.";
        } else if (lower.includes('export') || lower.includes('download')) {
            response = "You can export our conversation by clicking the 'Export' button at the top. Options include PDF download, text file, or email to yourself.";
        } else if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
            response = `Hello ${currentUser?.name || 'there'}! Welcome to The Wellness London. I'm here to help with health assessments, booking appointments, and connecting you with our medical team. How can I assist you today?`;
        } else {
            response = "I can help you with health assessments, booking appointments, or connecting you with our doctors. What would you like to know more about?";
        }

        addLiveTranscript(response, 'Wellness AI');
        conversationLog.push({ speaker: 'Wellness AI', text: response });
        
        if (speechSynth && !isMuted) {
            speakResponse(response);
        }
        
        trackEvent('local_response', { input: text, response: response });
    }, 1600);
}

// Speak response with British accent
function speakResponse(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 0.9;
    utterance.lang = 'en-GB';
    
    const voices = speechSynth.getVoices();
    const britishVoice = voices.find(voice => 
        voice.lang === 'en-GB' || 
        voice.name.includes('British') || 
        voice.name.includes('UK')
    );
    if (britishVoice) {
        utterance.voice = britishVoice;
    }
    
    speechSynth.speak(utterance);
}

// Transcript management
function addLiveTranscript(text, speaker, isInterim = false) {
    const container = document.getElementById('transcriptContainer');
    const hint = document.getElementById('startHint');
    if (hint) hint.remove();

    if (currentSpeaker !== speaker || !currentTranscriptBlock) {
        currentSpeaker = speaker;
        currentTranscriptBlock = document.createElement('div');
        currentTranscriptBlock.className = 'transcript-block';
        
        let speakerClass = 'user';
        if (speaker === 'Wellness AI') speakerClass = 'ai';
        if (speaker === 'Doctor') speakerClass = 'doctor';
        
        currentTranscriptBlock.innerHTML = `
            <div class="speaker-label ${speakerClass}">${speaker}</div>
            <div class="transcript-text"></div>
        `;
        container.appendChild(currentTranscriptBlock);
    }

    const textElement = currentTranscriptBlock.querySelector('.transcript-text');
    const words = text.split(' ');
    textElement.innerHTML = '';
    
    words.forEach((word, index) => {
        const wordSpan = document.createElement('span');
        wordSpan.className = `word ${isInterim ? 'interim' : ''}`;
        wordSpan.textContent = word;
        wordSpan.style.animationDelay = `${index * 0.08}s`;
        textElement.appendChild(wordSpan);
    });
    
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    const container = document.getElementById('transcriptContainer');
    const indicator = document.createElement('div');
    indicator.className = 'transcript-block';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = `
        <div class="speaker-label ai">Wellness AI</div>
        <div class="typing-indicator">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    container.appendChild(indicator);
    container.scrollTop = container.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

// Text input functions
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const text = input.value.trim();
    
    if (!text) return;
    
    addLiveTranscript(text, currentUser?.name || 'you', false);
    conversationLog.push({ speaker: currentUser?.name || 'you', text: text });
    
    input.value = '';
    processInput(text);
}

// Main functions
function initiateCall() {
    document.getElementById('mainScreen').classList.add('hidden');
    document.getElementById('callScreen').classList.add('active');
    
    callStartTime = Date.now();
    callTimer = setInterval(updateCallTimer, 1000);
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('bookingDate');
    if (dateInput) dateInput.setAttribute('min', today);
    
    // Auto-fill user info if registered
    if (currentUser && currentUser.type === 'registered') {
        const nameField = document.getElementById('bookingName');
        const emailField = document.getElementById('bookingEmail');
        const phoneField = document.getElementById('bookingPhone');
        
        if (nameField) nameField.value = currentUser.name || '';
        if (emailField) emailField.value = currentUser.email || '';
        if (phoneField) phoneField.value = currentUser.phone || '';
    }
    
    setTimeout(() => {
        document.getElementById('statusText').textContent = 'Connected';
        setupSpeech();
        isActive = true;
        
        if (recognition && !isMuted) {
            try {
                recognition.start();
            } catch (error) {
                logError(error, 'Starting recognition');
            }
        }

        // Welcome message
        setTimeout(() => {
            const userName = currentUser?.name || 'there';
            const welcomeText = `Hello ${userName}! Welcome to The Wellness London. I'm your AI health assistant. I can help assess your symptoms, book appointments, or connect you with our medical team. For any emergencies, please call 999 immediately. How can I help you today?`;
            
            addLiveTranscript(welcomeText, 'Wellness AI');
            conversationLog.push({ speaker: 'Wellness AI', text: welcomeText });
            
            if (speechSynth) {
                speakResponse(welcomeText);
            }
        }, 1000);
    }, 1500);
    
    trackEvent('call_initiated', { userType: currentUser?.type || 'guest' });
}

function terminateCall() {
    isActive = false;
    if (recognition) {
        recognition.stop();
    }
    if (speechSynth) {
        speechSynth.cancel();
    }
    
    clearInterval(callTimer);
    
    // Collect satisfaction feedback
    setTimeout(() => {
        const satisfaction = prompt('How would you rate your experience? (1-5 stars)');
        if (satisfaction && satisfaction >= 1 && satisfaction <= 5) {
            analytics.userSatisfaction = parseInt(satisfaction);
            trackEvent('satisfaction_rating', { rating: satisfaction });
        }
    }, 500);
    
    trackEvent('call_terminated', analytics);
    resetCall();
}

function resetCall() {
    document.getElementById('callScreen').classList.remove('active');
    document.getElementById('mainScreen').classList.remove('hidden');
    
    currentTranscriptBlock = null;
    currentSpeaker = null;
    conversationLog = [];
    callStartTime = null;
    selectedSymptoms = [];
    assessmentData = {};
    
    document.getElementById('transcriptContainer').innerHTML = '<div class="start-hint" id="startHint">Say "Hello" or type your health concern...</div>';
    document.getElementById('statusText').textContent = 'Connecting...';
    document.getElementById('callTimer').textContent = '0:00';
    
    // Reset assessment panel
    document.getElementById('assessmentPanel').classList.remove('active');
    document.querySelectorAll('.symptom-btn').forEach(btn => btn.classList.remove('selected'));
    document.getElementById('severitySlider').value = 5;
    document.getElementById('severityValue').textContent = '5';
}

function toggleMicrophone() {
    isMuted = !isMuted;
    const muteBtn = document.getElementById('muteButton');
    
    if (isMuted) {
        muteBtn.classList.add('active');
        if (recognition) recognition.stop();
        if (speechSynth) speechSynth.cancel();
        document.getElementById('statusText').textContent = 'Muted';
    } else {
        muteBtn.classList.remove('active');
        if (recognition && isActive) {
            try {
                recognition.start();
            } catch (error) {
                logError(error, 'Restarting recognition');
            }
        }
        document.getElementById('statusText').textContent = 'Listening';
    }
    
    trackEvent('microphone_toggled', { muted: isMuted });
}

function showBooking() {
    document.getElementById('bookingModal').classList.add('active');
    trackEvent('booking_modal_opened');
}

function hideBooking() {
    document.getElementById('bookingModal').classList.remove('active');
}

function showTerms() {
    alert('Terms of Service:\n\nThis is a medical consultation platform. Information provided is for educational purposes. Always consult qualified medical professionals for medical advice.\n\nWe comply with GDPR and UK data protection laws.');
}

function showPrivacy() {
    alert('Privacy Policy:\n\nYour data is encrypted and stored securely. We do not share personal information with third parties without consent. You have the right to request data deletion at any time.\n\nContact: privacy@thewellnesslondon.com');
}

// Load British voices and check API health on page load
window.addEventListener('DOMContentLoaded', async () => {
    // Load voices
    if (speechSynth) {
        speechSynth.onvoiceschanged = () => {
            const voices = speechSynth.getVoices();
            console.log('Available voices loaded:', voices.length);
        };
    }
    
    // Check API health
    try {
        const response = await fetch(`${API_URL}/health-check`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend API connected:', data.service);
        } else {
            console.warn('⚠️ Backend API not available, using local mode');
        }
    } catch (error) {
        console.warn('⚠️ Backend API not reachable, using local mode');
        console.log('To enable full features, run: python backend_api.py');
    }
    
    // Load saved user
    const savedUser = localStorage.getItem('wellnessUser');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            console.log('User restored:', currentUser.name);
        } catch (error) {
            logError(error, 'Failed to restore user');
        }
    }
    
    trackEvent('page_loaded');
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        if (document.getElementById('authModal').classList.contains('active')) {
            hideAuth();
        } else if (document.getElementById('bookingModal').classList.contains('active')) {
            hideBooking();
        } else if (document.getElementById('exportModal').classList.contains('active')) {
            hideExport();
        } else if (document.getElementById('callScreen').classList.contains('active')) {
            terminateCall();
        }
    }
    
    // Ctrl+E for export
    if (e.ctrlKey && e.key === 'e') {
        e.preventDefault();
        if (document.getElementById('callScreen').classList.contains('active')) {
            exportChat();
        }
    }
});

// Global error handlers
window.addEventListener('error', (event) => {
    logError({
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error
    }, 'Global error');
});

window.addEventListener('unhandledrejection', (event) => {
    logError({
        reason: event.reason,
        promise: event.promise
    }, 'Unhandled promise rejection');
});

// Periodic reminder check (every 30 minutes)
setInterval(() => {
    const reminders = JSON.parse(localStorage.getItem('appointmentReminders') || '[]');
    const now = new Date();
    
    reminders.forEach(reminder => {
        const reminderDate = new Date(reminder.reminderDate);
        const timeDiff = reminderDate - now;
        
        // Show reminder if within 1 hour
        if (timeDiff > 0 && timeDiff < 3600000) {
            showAppointmentReminder(reminder);
        }
    });
}, 1800000); // Check every 30 minutes

function showAppointmentReminder(reminder) {
    const message = `Reminder: You have a ${reminder.service} appointment tomorrow at ${reminder.appointmentTime}`;
    
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Appointment Reminder - The Wellness London', {
            body: message,
            icon: '/favicon.ico'
        });
    } else {
        alert(message);
    }
    
    trackEvent('reminder_shown', reminder);
}

// Request notification permission on first use
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}
