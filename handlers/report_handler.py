from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('attendance_reports.log'),
        logging.StreamHandler()
    ]
)

# --- Mock Database ---
report_db = {}
manager_db = {
    '254712345678': '254787654321'  # employee_phone: manager_phone
}

def ussd_response(text):
    return text

def _get_user_reports(phone: str) -> List[Dict]:
    """Fetches and sorts reports for a user."""
    reports = [r for r in report_db.values() if r.get('phone') == phone]
    return sorted(reports, key=lambda r: r['date'], reverse=True)

def _save_report(phone: str, status: str):
    """Saves a new report for the user."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    report_id = f"{phone}_{today_str}"
    report_db[report_id] = {
        'id': report_id,
        'phone': phone,
        'date': today_str,
        'status': status,
        'timestamp': datetime.now().isoformat()
    }
    logging.info(f"Report saved: {report_db[report_id]}")
    # In a real app, you would send SMS confirmations here

def handle_reporting(inputs: List[str], phone: str, session: Dict) -> Optional[str]:
    """Handles the reporting submenu."""
    stage = session.get('reporting_stage', 'menu')

    if stage == 'menu':
        if not inputs:
            return ussd_response(
                "CON Report Status:\n"
                "1. Daily Report\n"
                "2. Weekly Summary\n"
                "3. Log Absence\n"
                "0. Back"
            )
        
        choice = inputs[0]
        if choice == '0':
            return None  # Go back to main menu
        elif choice == '1':
            session['reporting_stage'] = 'daily_report'
            return ussd_response("END Your daily report will be sent via SMS.")
        elif choice == '2':
            session['reporting_stage'] = 'weekly_summary'
            return ussd_response("END Your weekly summary will be sent via SMS.")
        elif choice == '3':
            session['reporting_stage'] = 'log_absence'
            return ussd_response(
                "CON Log Absence:\n"
                "1. Sick Leave\n"
                "2. Emergency\n"
                "0. Back"
            )
        else:
            return ussd_response("CON Invalid option. Please try again.")

    elif stage == 'log_absence':
        if not inputs or len(inputs) < 2:
            return ussd_response("CON Invalid input for logging absence.")

        choice = inputs[1]
        if choice == '0':
            session['reporting_stage'] = 'menu'
            return handle_reporting([], phone, session) # Show previous menu
        
        absence_type = ""                
        if choice == '1':
            absence_type = "Sick Leave"
        elif choice == '2':
            absence_type = "Emergency"
        else:
            return ussd_response("CON Invalid absence type.")
        
        _save_report(phone, absence_type)
        session['reporting_stage'] = 'menu' # Reset stage
        return ussd_response(f"END Your absence ({absence_type}) has been logged.")

    # Default fallback
    return ussd_response("END An unexpected error occurred in reporting.")
