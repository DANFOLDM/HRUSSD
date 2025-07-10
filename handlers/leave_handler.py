from datetime import datetime, timedelta
import logging
from typing import Dict, Optional, List

# --- Configuration & Mock DB ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
leave_requests: Dict[str, Dict] = {}
LEAVE_TYPES = {
    '1': {'name': 'Sick Leave', 'max_days': 14},
    '2': {'name': 'Casual Leave', 'max_days': 5},
    '3': {'name': 'Annual Leave', 'max_days': 21}
}

def ussd_response(text):
    return text

# --- Sub-Handlers ---
def _handle_type_selection(inputs: List[str], session: Dict) -> Optional[str]:
    if not inputs:
        menu = "\n".join([f"{k}. {v['name']}" for k, v in LEAVE_TYPES.items()])
        return ussd_response(f"CON Select Leave Type:\n{menu}\n0. Back")
    
    choice = inputs[0]
    if choice == '0':
        return None # Go back
    
    if choice in LEAVE_TYPES:
        session['leave_stage'] = 'days'
        session['leave_type'] = choice
        return ussd_response(f"CON Enter number of days for {LEAVE_TYPES[choice]['name']}:")
    return ussd_response("CON Invalid leave type. Try again.")

def _handle_days_input(inputs: List[str], session: Dict) -> Optional[str]:
    if not inputs or not inputs[0].isdigit():
        return ussd_response("CON Please enter a valid number of days:")

    days = int(inputs[0])
    leave_type = LEAVE_TYPES[session['leave_type']]
    if 0 < days <= leave_type['max_days']:
        session['leave_stage'] = 'date'
        session['leave_days'] = days
        return ussd_response("CON Enter start date (DD-MM-YYYY):")
    return ussd_response(f"CON Invalid days. Max for {leave_type['name']} is {leave_type['max_days']}.")

def _handle_date_input(inputs: List[str], session: Dict) -> Optional[str]:
    if not inputs:
        return ussd_response("CON Please enter a start date (DD-MM-YYYY):")

    try:
        start_date = datetime.strptime(inputs[0], "%d-%m-%Y").date()
        if start_date < datetime.now().date():
            return ussd_response("CON Date cannot be in the past. Try again:")
        
        session['leave_stage'] = 'confirm'
        session['start_date'] = start_date.isoformat()
        
        leave_name = LEAVE_TYPES[session['leave_type']]['name']
        days = session['leave_days']
        date_str = start_date.strftime('%d %b, %Y')
        return ussd_response(f"CON Confirm Request:\n{days} days of {leave_name} starting {date_str}.\n1. Confirm\n0. Cancel")
    except ValueError:
        return ussd_response("CON Invalid date format. Use DD-MM-YYYY.")

def _handle_confirmation(inputs: List[str], phone: str, session: Dict) -> Optional[str]:
    if not inputs or inputs[0] not in ['1', '0']:
        return ussd_response("CON Invalid choice. 1 to confirm, 0 to cancel.")

    if inputs[0] == '0':
        session.clear() # Reset session
        return None # Go back to main menu

    request_id = f"LV-{phone[-4:]}-{int(datetime.now().timestamp() % 1000)}"
    leave_requests[request_id] = {
        'phone': phone,
        'type': LEAVE_TYPES[session['leave_type']]['name'],
        'days': session['leave_days'],
        'start_date': session['start_date'],
        'status': 'Pending Approval'
    }
    logging.info(f"Leave request submitted: {request_id}")
    from utils.sms_utils import SMSService
    sms_service = SMSService()
    sms_service.send_template(
        phone_number=phone,
        template_name="leave_approval",
        template_vars={
            "status": "Submitted",
            "type": LEAVE_TYPES[session['leave_type']]['name'],
            "days": session['leave_days']
        }
    )
    session.clear()
    return ussd_response(f"END Leave request {request_id} submitted successfully.")

# --- Main Handler ---
def handle_leave(inputs: List[str], phone: str, session: Dict) -> Optional[str]:
    """Handles the multi-step leave application process."""
    if 'leave_stage' not in session:
        session['leave_stage'] = 'type'

    stage = session['leave_stage']
    
    handler_map = {
        'type': _handle_type_selection,
        'days': _handle_days_input,
        'date': _handle_date_input,
        'confirm': _handle_confirmation
    }

    handler = handler_map.get(stage)
    if handler:
        # Pass only the relevant part of inputs
        input_for_stage = inputs[1:] if stage != 'type' and inputs else inputs
        return handler(input_for_stage, session if stage != 'confirm' else phone, session)

    return ussd_response("END An unexpected error occurred in the leave module.")
