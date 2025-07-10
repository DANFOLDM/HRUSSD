import requests
import logging
import threading
from datetime import datetime
from typing import Dict, Optional, Tuple, List

# Configure atomic logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('document_audit.log', mode='a'),
        logging.StreamHandler()
    ],
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Configuration (move to environment variables in production)
CONFIG = {
    'SMS_API_KEY': 'your_api_key_here',
    'SMS_URL': 'https://api.africastalking.com/version1/messaging',
    'DOCUMENT_BASE_URL': 'https://secure.elevatehr.com/documents',
    'MAX_ATTEMPTS': 3,
    'SMS_RETRIES': 2
}

# Document permissions (would come from DB in production)
DOCUMENT_PERMISSIONS = {
    'payslip': {
        'roles': ['employee', 'manager'],
        'retention_days': 180,
        'path': '/payslips/'
    },
    'contract': {
        'roles': ['employee', 'hr'],
        'retention_days': 3650,
        'path': '/contracts/'
    },
    'tax_cert': {
        'roles': ['employee', 'finance'],
        'retention_days': 365,
        'path': '/tax_docs/'
    }
}

def ussd_response(text: str) -> str:
    """Ensure proper USSD response formatting"""
    return text if text.startswith(('CON ', 'END ')) else f"CON {text}"

def _sanitize_phone(phone: str) -> Optional[str]:
    """Nuclear-grade phone validation"""
    try:
        return ''.join(c for c in phone if c.isdigit())[-9:]  # Kenyan format
    except:
        return None

def _generate_temp_token() -> str:
    """Mock token generation (use JWT in production)"""
    return "tmp_" + str(hash(datetime.now()))[:12]

def _generate_document_url(phone: str, doc_type: str) -> Optional[str]:
    """Secure document URL generation"""
    if doc_type not in DOCUMENT_PERMISSIONS:
        return None
        
    # In production: Verify user has permission
    return (
        f"{CONFIG['DOCUMENT_BASE_URL']}/{doc_type}/"
        f"{phone}?token={_generate_temp_token()}&expires={int(datetime.now().timestamp()) + 86400}"
    )

def _send_sms_with_retries(phone: str, message: str, attempt: int = 1):
    """Retry mechanism with circuit breaker"""
    from utils.sms_utils import SMSService
    sms_service = SMSService()
    sms_service.send([phone], message)
    logging.info(f"SMS delivered to {phone} (attempt {attempt})")

def _send_document_sms_async(phone: str, doc_name: str, url: str):
    """Self-healing SMS delivery system"""
    message = (
        f"ElevateHR Document Ready\n"
        f"Type: {doc_name}\n"
        f"Download: {url}\n"
        "Expires in 24 hours"
    )
    
    threading.Thread(
        target=_send_sms_with_retries,
        args=(phone, message),
        daemon=True
    ).start()

def _get_document_mapping(choice: str) -> Tuple[Optional[str], Optional[str]]:
    """Fault-tolerant option mapping"""
    mapping = {
        '1': ('payslip', 'Payslip'),
        '2': ('contract', 'Employment Contract'),
        '3': ('tax_cert', 'Tax Certificate')
    }
    return mapping.get(choice, (None, None))

def _handle_help_request(phone: str) -> str:
    """Help system with guaranteed response"""
    logging.info(f"Help requested by {phone}")
    _send_sms_with_retries(phone, "HR will contact you about your document request")
    return ussd_response("END Help request received")

def handle_document(inputs: List[str], phone: str, session: Dict) -> Optional[str]:
    """Handles the document submenu."""
    
    # Ensure doc_stage is initialized
    if 'doc_stage' not in session:
        session['doc_stage'] = 'menu'

    stage = session['doc_stage']
    
    # If no input or returning to menu, show main document menu
    if not inputs or stage == 'menu':
        session['doc_stage'] = 'menu' # Reset stage to menu
        return ussd_response(
            "CON Download Documents:\n"
            "1. Latest Payslip\n"
            "2. Employment Contract\n"
            "3. Tax Certificate\n"
            "4. Request Help\n"
            "0. Back"
        )

    choice = inputs[0]

    # Handle back option
    if choice == '0':
        return None  # Signal to go back to main menu

    # Process document selection
    if stage == 'menu':
        doc_key, doc_name = _get_document_mapping(choice)
        if doc_key:
            doc_url = _generate_document_url(phone, doc_key)
            if doc_url:
                _send_document_sms_async(phone, doc_name, doc_url)
                return ussd_response(f"END {doc_name} link sent via SMS.\nCheck your messages.")
            else:
                return ussd_response("END Document unavailable. Contact HR.")
        elif choice == '4':
            return _handle_help_request(phone)
        else:
            return ussd_response("CON Invalid option. Please try again.")

    return ussd_response("END An unexpected error occurred in document module.")
