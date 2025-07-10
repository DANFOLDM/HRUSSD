from datetime import datetime, timedelta
import logging
from typing import Dict, Optional, Tuple
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('clock_utils.log'),
        logging.StreamHandler()
    ]
)

# Configuration
CONFIG = {
    'DATA_FILE': 'clock_records.json',
    'WORK_HOURS': 8,
    'SMS_ENABLED': True
}

# In-memory storage with file backup
_clock_records: Dict[str, Dict] = {}

def init_clock_system():
    """Initialize clock system with data persistence"""
    global _clock_records
    try:
        if os.path.exists(CONFIG['DATA_FILE']):
            with open(CONFIG['DATA_FILE'], 'r') as f:
                _clock_records = json.load(f)
        logging.info("Clock system initialized with persistence")
    except Exception as e:
        logging.error(f"Data load failed: {str(e)}")
        _clock_records = {}

def clock_in(phone: str) -> Tuple[str, bool]:
    """
    Record clock-in with full validation
    Returns: (response_message, success_status)
    """
    try:
        now = datetime.now()
        today = now.date().isoformat()
        
        # Check existing clock-in
        if phone in _clock_records and _clock_records[phone].get('date') == today:
            return "You've already clocked in today", False
        
        # Record clock-in
        _clock_records[phone] = {
            'phone': phone,
            'clock_in': now.isoformat(),
            'date': today,
            'status': 'clocked_in'
        }
        
        _save_data()
        
        # Prepare response
        clock_in_time = now.strftime("%I:%M %p")
        expected_out = (now + timedelta(hours=CONFIG['WORK_HOURS'])).strftime("%I:%M %p")
        
        message = (
            f"Clock-in recorded at {clock_in_time}\n"
            f"Expected clock-out: {expected_out}"
        )
        
        # Send SMS notification
        if CONFIG['SMS_ENABLED']:
            _send_sms_notification(
                phone,
                f"Clocked IN at {clock_in_time}\nExpected OUT: {expected_out}"
            )
        
        return message, True
        
    except Exception as e:
        logging.error(f"Clock-in failed for {phone}: {str(e)}")
        return "System error. Your clock-in was recorded", False

def clock_out(phone: str) -> Tuple[str, bool]:
    """
    Record clock-out with duration calculation
    Returns: (response_message, success_status)
    """
    try:
        now = datetime.now()
        today = now.date().isoformat()
        
        # Validate existing clock-in
        if phone not in _clock_records or _clock_records[phone].get('date') != today:
            return "Please clock in first", False
            
        if 'clock_out' in _clock_records[phone]:
            return "You've already clocked out today", False
            
        # Calculate duration
        clock_in_time = datetime.fromisoformat(_clock_records[phone]['clock_in'])
        duration = now - clock_in_time
        hours, minutes = _calculate_duration(duration)
        
        # Record clock-out
        _clock_records[phone].update({
            'clock_out': now.isoformat(),
            'duration_hours': hours,
            'duration_minutes': minutes,
            'status': 'clocked_out'
        })
        
        _save_data()
        
        # Prepare response
        clock_out_time = now.strftime("%I:%M %p")
        message = (
            f"Clock-out recorded at {clock_out_time}\n"
            f"Work duration: {hours}h {minutes}m\n"
            f"IN: {clock_in_time.strftime('%I:%M %p')}"
        )
        
        # Send SMS notification
        if CONFIG['SMS_ENABLED']:
            _send_sms_notification(
                phone,
                f"Clocked OUT at {clock_out_time}\nWorked: {hours}h {minutes}m"
            )
        
        return message, True
        
    except Exception as e:
        logging.error(f"Clock-out failed for {phone}: {str(e)}")
        return "System error. Your clock-out was recorded", False

def get_today_status(phone: str) -> Optional[Dict]:
    """Get today's clock status with validation"""
    today = datetime.now().date().isoformat()
    if phone in _clock_records and _clock_records[phone].get('date') == today:
        return _clock_records[phone]
    return None

# --- Helper Functions ---

def _calculate_duration(duration: timedelta) -> Tuple[int, int]:
    """Convert timedelta to hours and minutes"""
    total_seconds = duration.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    return hours, minutes

def _send_sms_notification(phone: str, message: str) -> bool:
    """Mock SMS notification function"""
    try:
        # In production, integrate with SMS gateway
        logging.info(f"SMS Notification to {phone}: {message}")
        return True
    except Exception as e:
        logging.error(f"SMS failed for {phone}: {str(e)}")
        return False

def _save_data() -> None:
    """Persist data to file"""
    try:
        with open(CONFIG['DATA_FILE'], 'w') as f:
            json.dump(_clock_records, f, indent=2)
    except Exception as e:
        logging.error(f"Data save failed: {str(e)}")

# Initialize system on import
init_clock_system()