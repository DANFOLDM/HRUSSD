from datetime import datetime, timedelta
import threading
import logging
from typing import Dict, Optional, List

# --- Failsafe Logging ---
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler('clock_system_audit.log'), logging.StreamHandler()],
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# --- Mock Database & Config ---
clock_records: Dict[str, Dict] = {}
CONFIG = {'MAX_WORK_HOURS': 8, 'SMS_ENABLED': True}
_transaction_lock = threading.Lock()

def ussd_response(text):
    return text

# --- Core Clock-in/Out Logic ---
def _get_user_record(phone: str) -> Dict:
    return clock_records.get(phone, {})

def _create_time_record(time: datetime) -> Dict:
    return {'time': time, 'time_str': time.strftime('%I:%M %p')}

def _process_clock_in(phone: str, now: datetime) -> str:
    with _transaction_lock:
        clock_records[phone] = {
            'clock_in': _create_time_record(now),
            'last_action': 'in'
        }
    expected_out = (now + timedelta(hours=CONFIG['MAX_WORK_HOURS'])).strftime('%I:%M %p')
    from utils.sms_utils import SMSService
    sms_service = SMSService()
    sms_service.send_template(
        phone_number=phone,
        template_name="clock_confirm",
        template_vars={
            "action": "IN",
            "time": now.strftime('%I:%M %p'),
            "date": now.strftime('%Y-%m-%d')
        }
    )
    return ussd_response(f"END Clocked IN at {now.strftime('%I:%M %p')}. Expected OUT: {expected_out}")

def _process_clock_out(phone: str, now: datetime, record: Dict) -> str:
    with _transaction_lock:
        record['clock_out'] = _create_time_record(now)
        record['last_action'] = 'out'
        duration = now - record['clock_in']['time']
        hours, rem = divmod(duration.seconds, 3600)
        minutes, _ = divmod(rem, 60)
    from utils.sms_utils import SMSService
    sms_service = SMSService()
    sms_service.send_template(
        phone_number=phone,
        template_name="clock_confirm",
        template_vars={
            "action": "OUT",
            "time": now.strftime('%I:%M %p'),
            "date": now.strftime('%Y-%m-%d')
        }
    )
    return ussd_response(f"END Clocked OUT at {now.strftime('%I:%M %p')}. Worked: {hours}h {minutes}m.")

# --- Main Handler ---
def handle_clock(inputs: List[str], phone: str, session: Dict) -> Optional[str]:
    """Handles the clock-in/out submenu."""
    now = datetime.now()
    user_record = _get_user_record(phone)
    action = 'out' if user_record.get('last_action') == 'in' else 'in'

    if not inputs:
        status = "Clocked Out" if action == 'in' else "Clocked In"
        prompt = f"Clock In" if action == 'in' else f"Clock Out"
        return ussd_response(
            f"CON Clock System\nStatus: {status}\n\n1. {prompt}\n0. Back"
        )

    choice = inputs[0]
    if choice == '0':
        return None  # Go back to main menu
    
    if choice == '1':
        if action == 'in':
            # Prevent re-clocking in if already done for the day
            if user_record.get('last_action') == 'out' and user_record.get('clock_out'):
                 return ussd_response("END You have already clocked in and out for the day.")
            return _process_clock_in(phone, now)
        else:
            return _process_clock_out(phone, now, user_record)
    
    return ussd_response("CON Invalid option. Please try again.")