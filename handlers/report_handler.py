from datetime import datetime

# Simulated report database
report_db = {}

def handle_reporting(inputs, phone, session):
    level = len(inputs)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Main report menu
    if level == 0:
        session['stage'] = 'report_main'
        session['report_date'] = today
        return ussd_response(
            "CON Report Status:\n"
            "1. Present at work\n"
            "2. Working remotely\n"
            "3. Sick leave\n"
            "4. On approved leave\n"
            "5. Unexpected absence\n"
            "6. View/Edit reports"
        )
    
    # Handle status selection
    elif level == 1 and session.get('stage') == 'report_main':
        choice = inputs[0]
        
        if choice == '6':  # View/Edit reports
            session['stage'] = 'report_history'
            return _show_report_history(phone)
        
        status_map = {
            '1': ("Present", "at workplace"),
            '2': ("Remote", "working from alternate location"),
            '3': ("Sick", "on sick leave"),
            '4': ("On Leave", "on approved leave"),
            '5': ("Absent", "unexpected absence")
        }
        
        if choice in status_map:
            status, description = status_map[choice]
            session['selected_status'] = status
            session['stage'] = 'report_confirm'
            
            # Check if already reported today
            if phone in report_db and report_db[phone].get('date') == today:
                current_status = report_db[phone]['status']
                return ussd_response(
                    f"CON You're currently marked as {current_status}.\n"
                    f"Change to {status}?\n"
                    "1. Yes\n"
                    "2. No"
                )
            else:
                return ussd_response(
                    f"CON Confirm {status} status:\n"
                    f"{description}\n\n"
                    "1. Confirm\n"
                    "2. Cancel"
                )
    
    # Handle confirmation
    elif level == 2 and session.get('stage') == 'report_confirm':
        if inputs[1] == '1':  # User confirmed
            status = session.get('selected_status')
            report_db[phone] = {
                'date': today,
                'status': status,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            return ussd_response(
                f"END Status recorded:\n"
                f"{status} on {today}\n\n"
                "Reply 'REPORT' to update."
            )
        else:
            return ussd_response("END Status update cancelled.")
    
    # Handle report history
    elif session.get('stage') == 'report_history':
        if level == 1 and inputs[0] == '0':  # Back option
            session['stage'] = 'report_main'
            return handle_reporting([], phone, session)
        
        # Show detailed report for selected date
        if level == 2 and inputs[0] == '1':
            date_index = int(inputs[1]) - 1
            user_reports = [r for r in report_db.values() if r.get('phone') == phone]
            if 0 <= date_index < len(user_reports):
                report = user_reports[date_index]
                session['edit_date'] = report['date']
                return ussd_response(
                    f"CON Report for {report['date']}:\n"
                    f"Status: {report['status']}\n"
                    f"Time: {report['timestamp']}\n\n"
                    "1. Edit\n"
                    "2. Delete\n"
                    "0. Back"
                )
    
    return ussd_response("END Invalid selection. Please try again.")

def _show_report_history(phone):
    """Helper function to display report history"""
    user_reports = [r for r in report_db.values() if r.get('phone') == phone]
    
    if not user_reports:
        return ussd_response("END No reports found.")
    
    menu_items = []
    for i, report in enumerate(user_reports[-5:], 1):  # Show last 5 reports
        menu_items.append(f"{i}. {report['date']}: {report['status']}")
    
    menu_text = "\n".join(menu_items)
    return ussd_response(
        f"CON Your Reports (Last 5):\n"
        f"{menu_text}\n\n"
        "Select to view details\n"
        "0. Back to main menu"
    )

def ussd_response(text):
    return f"{text}"