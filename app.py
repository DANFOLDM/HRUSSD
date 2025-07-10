from flask import Flask, request, jsonify
from functools import wraps
from handlers.main_menu import handle_main_menu
from sessions import get_user_session, update_user_session, cleanup_old_sessions, _sessions
import logging
from datetime import datetime
from utils.rate_limiter import RateLimiter
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

# Configuration
class Config:
    AT_SANDBOX = False  # Set to False for production
    AT_SANDBOX_NUMBER = '+254711082000'
    AT_USERNAME = ''  # <<< REPLACE WITH YOUR AFRICA'S TALKING USERNAME
    AT_API_KEY = ''    # <<< REPLACE WITH YOUR AFRICA'S TALKING API KEY

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('ussd_gateway.log'),
        logging.StreamHandler()
    ]
)

# Initialize rate limiter
limiter = RateLimiter(max_requests=10, period_seconds=60)

def log_ussd_interaction(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = datetime.now()
        try:
            response = f(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            
            logging.info(
                f"USSD Request - Session: {request.form.get('sessionId')} | "
                f"Phone: {request.form.get('phoneNumber')} | "
                f"Input: '{request.form.get('text', '')}' | "
                f"Response: '{response}' | "
                f"Processed in {duration:.2f}s"
            )
            return response
        except Exception as e:
            logging.error(f"USSD Error: {str(e)}")
            return "END System error. Please try again."
    return decorated_function

@app.route('/ussd', methods=['POST'])
@log_ussd_interaction
def ussd():
    # Validate required parameters
    required_fields = ['sessionId', 'phoneNumber', 'serviceCode']
    if not all(field in request.form for field in required_fields):
        logging.warning("Missing required USSD parameters")
        return "END Invalid request parameters"

    session_id = request.form['sessionId']
    phone_number = request.form['phoneNumber']
    text_input = request.form.get('text', '').strip()
    service_code = request.form['serviceCode']

    # Rate limiting check
    if not limiter.is_allowed(phone_number):
        logging.warning(f"Rate limit exceeded for {phone_number}")
        return "END Too many requests. Please try again later."

    try:
        # Session management
        session = get_user_session(session_id)
        
        # Sandbox handling
        if Config.AT_SANDBOX and phone_number != Config.AT_SANDBOX_NUMBER:
            session['real_phone'] = phone_number  # Store actual number
            phone_number = Config.AT_SANDBOX_NUMBER  # Process as sandbox number
        
        # Process USSD input
        response = handle_main_menu(
            inputs=text_input.split('*') if text_input else [],
            phone=phone_number,
            session=session
        )
        
        # Update session
        update_user_session(session_id, session)
        
        return response

    except Exception as e:
        logging.critical(
            f"USSD Processing Failed - "
            f"Session: {session_id} | "
            f"Phone: {phone_number} | "
            f"Error: {str(e)}"
        )
        return "END System error. Please try again."

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(_sessions),
        "mode": "sandbox" if Config.AT_SANDBOX else "production"
    })

def cleanup_sessions():
    """Regular session cleanup job"""
    with app.app_context():
        try:
            deleted = cleanup_old_sessions()
            logging.info(f"Cleaned up {deleted} stale sessions")
        except Exception as e:
            logging.error(f"Session cleanup failed: {str(e)}")

if __name__ == '__main__':
    # Initialize scheduler with timezone
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Africa/Nairobi'))
    scheduler.add_job(cleanup_sessions, 'interval', minutes=30)
    scheduler.start()
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    finally:
        scheduler.shutdown()
