import os
import logging
from dotenv import load_dotenv
import africastalking
from typing import List, Dict, Optional
from time import sleep
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('sms_service.log'),
        logging.StreamHandler()
    ]
)

# Initialize Africa's Talking only if not in sandbox mode
if not Config.AT_SANDBOX:
    try:
        africastalking.initialize(
            username=Config.AT_USERNAME,
            api_key=Config.AT_API_KEY
        )
        sms = africastalking.SMS
        logging.info("SMS service initialized in LIVE mode")
    except Exception as e:
        logging.critical(f"Failed to initialize SMS service: {str(e)}")
        sms = None
else:
    sms = None
    logging.info("SMS service running in SANDBOX mode")

class SMSService:
    @staticmethod
    def send(phone_numbers: List[str], message: str, sender_id: Optional[str] = None) -> Dict:
        """Send SMS with sandbox detection"""
        if Config.AT_SANDBOX:
            real_phones = phone_numbers  # Will be logged but not actually sent
            logging.info(f"[SANDBOX] SMS would send to {real_phones}: {message[:60]}...")
            return {"status": "sandbox_simulated"}
        
        if not sms:
            return {"status": "error", "message": "SMS service not initialized"}

        try:
            response = sms.send(message, phone_numbers, sender_id)
            logging.info(f"SMS sent to {phone_numbers}. Response: {response}")
            return {"status": "success", "response": response}
        except Exception as e:
            logging.error(f"SMS failed to {phone_numbers}: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}

    @staticmethod
    def send_template(phone_number: str, template_name: str, template_vars: Dict) -> Dict:
        """Send templated SMS"""
        templates = {
            "welcome": "Welcome {name} to ElevateHR! Your ID: {id}",
            "clock_confirm": "Clocked {action} at {time} on {date}",
            "leave_approval": "Leave {status}: {type} for {days} days"
        }
        
        if template_name not in templates:
            return {"status": "error", "message": "Invalid template"}
        
        try:
            message = templates[template_name].format(**template_vars)
            return SMSService.send([phone_number], message)
        except KeyError as e:
            return {"status": "error", "message": f"Missing template variable: {str(e)}"}

# Singleton instance
sms_handler = SMSService()