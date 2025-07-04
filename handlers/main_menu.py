from handlers.clock_handler import handle_clock
from handlers.leave_handler import handle_leave
from handlers.performance_handler import handle_performance
from handlers.report_handler import handle_reporting
from handlers.document_handler import handle_document

# Configuration constants
MAX_ATTEMPTS = 3
SESSION_TIMEOUT = 300  # 5 minutes in seconds

def handle_main_menu(text, session, phone):
    try:
        inputs = text.split('*') if text else []
        level = len(inputs)
        
        # Initialize session if new
        if 'init_time' not in session:
            session.update({
                'init_time': time.time(),
                'attempts': 0,
                'stage': 'main'
            })
        
        # Check session timeout
        if time.time() - session['init_time'] > SESSION_TIMEOUT:
            return ussd_response("END Session expired. Please dial again.")
        
        # Main menu handler
        if level == 0 or session.get('stage') == 'main':
            if level > 0:
                choice = inputs[0]
                menu_options = {
                    '1': {'handler': handle_clock, 'stage': 'clock'},
                    '2': {'handler': handle_reporting, 'stage': 'report'},
                    '3': {'handler': handle_leave, 'stage': 'leave'},
                    '4': {'handler': handle_performance, 'stage': 'performance'},
                    '5': {'message': "END Your payment summary will be sent via SMS."},
                    '6': {'handler': handle_document, 'stage': 'docs'}
                }
                
                if choice in menu_options:
                    option = menu_options[choice]
                    if 'handler' in option:
                        session['stage'] = option['stage']
                        return option['handler'](inputs[1:], phone, session)
                    return ussd_response(option['message'])
                
                session['attempts'] += 1
                if session['attempts'] >= MAX_ATTEMPTS:
                    return ussd_response("END Too many invalid attempts. Goodbye.")
                
            return ussd_response(
                "CON Welcome to ElevateHR\n"
                "1. Clock In/Out\n"
                "2. Report Status\n"
                "3. Request Leave\n"
                "4. Performance Summary\n"
                "5. Payment Summary\n"
                "6. Download Documents\n"
                "0. Exit"
            )
        
        # Handle sub-menu stages
        current_stage = session.get('stage')
        if current_stage == 'clock':
            return handle_clock(inputs, phone, session)
        elif current_stage == 'report':
            return handle_reporting(inputs, phone, session)
        elif current_stage == 'leave':
            return handle_leave(inputs, phone, session)
        elif current_stage == 'performance':
            return handle_performance(inputs, phone, session)
        elif current_stage == 'docs':
            return handle_document(inputs, phone, session)
        
        return ussd_response("END Invalid session state. Please dial again.")
    
    except Exception as e:
        # Log the actual error for debugging
        print(f"USSD Error: {str(e)}")
        return ussd_response("END System error. Please try again later.")

def ussd_response(text):
    """Enhanced response formatter with proper USSD protocol handling"""
    # Add any carrier-specific formatting if needed
    return text

# Example of adding time (if not already imported)
import time