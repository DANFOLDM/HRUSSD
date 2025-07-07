from datetime import datetime, timedelta

# Temporary storage - replace with database in production
clock_records = {}

def handle_clock(inputs, phone, session):
    """Handle both clock-in and clock-out with immediate action"""
    now = datetime.now()
    today = now.date()
    
    # Get existing record if any
    user_record = clock_records.get(phone, {})
    
    # If user hasn't clocked in today or has already clocked out
    if 'clock_in' not in user_record or user_record['clock_in'].date() != today:
        return process_clock_in(phone, now)
    elif 'clock_out' not in user_record:
        return process_clock_out(phone, now, user_record)
    else:
        return show_clock_status(user_record)

def process_clock_in(phone, now):
    """Handle clock-in operation"""
    clock_records[phone] = {
        'clock_in': now,
        'last_action': 'in'
    }
    return ussd_response(
        f"END Clocked IN at {now.strftime('%I:%M %p')}\n"
        f"Expected OUT: {(now + timedelta(hours=8)).strftime('%I:%M %p')}"
    )

def process_clock_out(phone, now, user_record):
    """Handle clock-out operation"""
    clock_records[phone]['clock_out'] = now
    clock_records[phone]['last_action'] = 'out'
    
    duration = now - user_record['clock_in']
    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60
    
    return ussd_response(
        f"END Clocked OUT at {now.strftime('%I:%M %p')}\n"
        f"Work duration: {hours}h {minutes}m"
    )

def show_clock_status(record):
    """Show completed clock status"""
    return ussd_response(
        "END Today's clocking complete:\n"
        f"IN: {record['clock_in'].strftime('%I:%M %p')}\n"
        f"OUT: {record['clock_out'].strftime('%I:%M %p')}"
    )

def ussd_response(text):
    return text