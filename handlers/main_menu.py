from handlers.clock_handler import handle_clock
from handlers.leave_handler import handle_leave
from handlers.performance_handler import handle_performance
from handlers.report_handler import handle_reporting
from handlers.document_handler import handle_document
import time

# Configuration constants
MAX_ATTEMPTS = 3
SESSION_TIMEOUT = 300  # 5 minutes in seconds

# Hardcoded employee data
EMPLOYEE_DATA = {
    '1': {'name': 'John Doe', 'department': 'IT', 'position': 'Software Developer'},
    '2': {'name': 'Jane Smith', 'department': 'HR', 'position': 'HR Manager'},
    '3': {'name': 'Mike Johnson', 'department': 'Finance', 'position': 'Accountant'},
    '4': {'name': 'Sarah Wilson', 'department': 'Marketing', 'position': 'Marketing Specialist'},
    '5': {'name': 'David Brown', 'department': 'Operations', 'position': 'Operations Manager'}
}

def handle_main_menu(text, session, phone):
    try:
        inputs = text.split('*') if text else []
        level = len(inputs)
        
        # Initialize session if new
        if 'init_time' not in session:
            session.update({
                'init_time': time.time(),
                'attempts': 0,
                'stage': 'auth',  # Start with authentication
                'employee_id': None,
                'employee_name': None
            })
        
        # Check session timeout
        if time.time() - session['init_time'] > SESSION_TIMEOUT:
            return ussd_response("END Session expired. Please dial again.")
        
        # Authentication stage - Employee ID input
        if session.get('stage') == 'auth':
            if level == 0:
                # First interaction - ask for employee ID
                return ussd_response("CON Welcome to ElevateHR\nPlease enter your Employee ID:")
            else:
                # User has entered an employee ID
                employee_id = inputs[0]
                
                if employee_id in EMPLOYEE_DATA:
                    # Valid employee ID
                    session['employee_id'] = employee_id
                    session['employee_name'] = EMPLOYEE_DATA[employee_id]['name']
                    session['stage'] = 'main'
                    session['attempts'] = 0  # Reset attempts for main menu
                    
                    # Show main menu with personalized greeting
                    return ussd_response(
                        f"CON Welcome {session['employee_name']}\n"
                        "1. Clock In/Out\n"
                        "2. Report Status\n"
                        "3. Request Leave\n"
                        "4. Performance Summary\n"
                        "5. Payment Summary\n"
                        "6. Download Documents\n"
                        "0. Exit"
                    )
                else:
                    # Invalid employee ID
                    session['attempts'] += 1
                    if session['attempts'] >= MAX_ATTEMPTS:
                        return ussd_response("END Too many invalid attempts. Goodbye.")
                    
                    return ussd_response(
                        f"CON Invalid Employee ID. Please try again.\n"
                        f"Attempts remaining: {MAX_ATTEMPTS - session['attempts']}\n"
                        "Enter your Employee ID:"
                    )
        
        # Main menu handler (after authentication)
        elif session.get('stage') == 'main':
            if level == 1:
                # User is selecting from main menu
                choice = inputs[0]
                menu_options = {
                    '1': {'handler': handle_clock, 'stage': 'clock'},
                    '2': {'handler': handle_reporting, 'stage': 'report'},
                    '3': {'handler': handle_leave, 'stage': 'leave'},
                    '4': {'handler': handle_performance, 'stage': 'performance'},
                    '5': {'message': "END Your payment summary will be sent via SMS."},
                    '6': {'handler': handle_document, 'stage': 'docs'},
                    '0': {'message': "END Thank you for using ElevateHR. Goodbye!"}
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
                    f"CON Invalid option. Please try again.\n"
                    f"Welcome {session['employee_name']}\n"
                    "1. Clock In/Out\n"
                    "2. Report Status\n"
                    "3. Request Leave\n"
                    "4. Performance Summary\n"
                    "5. Payment Summary\n"
                    "6. Download Documents\n"
                    "0. Exit"
                )
            else:
                # Show main menu again if user just pressed * without selection
                return ussd_response(
                    f"CON Welcome {session['employee_name']}\n"
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

def get_employee_info(employee_id):
    """Helper function to get employee information"""
    return EMPLOYEE_DATA.get(employee_id, None)

def is_valid_employee(employee_id):
    """Helper function to validate employee ID"""
    return employee_id in EMPLOYEE_DATA
