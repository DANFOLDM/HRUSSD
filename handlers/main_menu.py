from handlers.clock_handler import handle_clock
from handlers.leave_handler import handle_leave
from handlers.performance_handler import handle_performance
from handlers.report_handler import handle_reporting
from handlers.document_handler import handle_document
from utils.sms_utils import SMSService
import logging
import time

# Configuration
MAX_ATTEMPTS = 3
SESSION_TIMEOUT = 300  # 5 minutes
VALID_JOB_IDS = {'EMP123', 'EMP456', 'MGR789'}

sms = SMSService()

def ussd_response(text):
    """Ensure proper USSD response formatting."""
    return text if text.startswith(('CON ', 'END ')) else f"CON {text}"

def show_main_menu(session, error_msg=None):
    """Generates the main menu string."""
    menu_text = [
        f"CON Main Menu\nSigned in as: {session.get('emp_id', 'Unknown')}",
    ]
    if error_msg:
        menu_text.append(f"\n{error_msg}")
    
    menu_text.extend([
        "\n",
        "1. Clock In/Out",
        "2. Report Status",
        "3. Request Leave",
        "4. Performance",
        "5. Payment Summary",
        "6. Documents",
        "0. Exit"
    ])
    return "\n".join(menu_text)

def handle_main_menu(inputs, phone, session):
    try:
        # Initialize session if it's new
        if 'init_time' not in session:
            session.update({
                'init_time': time.time(),
                'stage': 'auth',
                'auth_attempts': 0
            })

        # Check for session timeout
        if time.time() - session.get('init_time', 0) > SESSION_TIMEOUT:
            return ussd_response("END Session expired. Please dial again.")

        # --- Authentication Stage ---
        if session.get('stage') == 'auth':
            if not inputs:
                return ussd_response("CON Welcome to ElevateHR\nPlease enter your Employee ID:")
            
            emp_id = inputs[0].upper().strip()
            if emp_id in VALID_JOB_IDS:
                session['authenticated'] = True
                session['emp_id'] = emp_id
                session['stage'] = 'main_menu'
                return show_main_menu(session)
            else:
                session['auth_attempts'] += 1
                if session['auth_attempts'] >= MAX_ATTEMPTS:
                    return ussd_response("END Too many invalid attempts. Goodbye.")
                remaining = MAX_ATTEMPTS - session['auth_attempts']
                return ussd_response(f"CON Invalid ID. {remaining} attempts left.\nEnter Employee ID:")

        if not session.get('authenticated'):
            return ussd_response("END Authentication failed. Please dial again.")

        # --- Menu Navigation ---
        menu_inputs = inputs[1:] if len(inputs) > 1 else []
        stage = session.get('stage', 'main_menu')

        if stage == 'main_menu':
            if not menu_inputs:
                return show_main_menu(session)

            choice = menu_inputs[0]
            
            menu_options = {
                '1': 'clock_menu',
                '2': 'report_menu',
                '3': 'leave_menu',
                '4': 'performance_menu',
                '6': 'docs_menu',
            }

            if choice == '0':
                return ussd_response("END Thank you for using ElevateHR.")
            elif choice == '5':
                return ussd_response("END Your payment summary will be sent via SMS.")
            elif choice in menu_options:
                session['stage'] = menu_options[choice]
                stage = session['stage']
                menu_inputs = menu_inputs[1:]
            else:
                return show_main_menu(session, "Invalid option. Try again:")

        # --- Submenu Stages ---
        submenu_handlers = {
            'clock_menu': handle_clock,
            'report_menu': handle_reporting,
            'leave_menu': handle_leave,
            'performance_menu': handle_performance,
            'docs_menu': handle_document
        }

        if stage in submenu_handlers:
            handler = submenu_handlers[stage]
            response = handler(menu_inputs, phone, session)
            
            if response is None:
                session['stage'] = 'main_menu'
                return show_main_menu(session)
            return response

        return ussd_response("END An unexpected error occurred. Please try again.")

    except Exception as e:
        logging.error(f"Main Menu Error: {e}", exc_info=True)
        return ussd_response("END System error. Please try again later.")