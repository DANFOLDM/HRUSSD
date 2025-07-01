from datetime import datetime, timedelta

# Simulated in-memory user clock-in/out log
user_clock_log = {}

def handle_clock(inputs, phone, session):
    """Handle both clock-in and clock-out operations"""
    level = len(inputs)
    
    if level == 0:
        session['stage'] = 'clock_choice'
        return ussd_response("CON Clock Options:\n1. Clock In\n2. Clock Out")
    
    elif session.get('stage') == 'clock_choice':
        choice = inputs[0]
        if choice == '1':
            return clock_in(phone)
        elif choice == '2':
            return clock_out(phone)
        else:
            return ussd_response("CON Invalid choice. Try again.\n1. Clock In\n2. Clock Out")
    
    return ussd_response("END Something went wrong with clock operations.")

def clock_in(phone):
    now = datetime.now()
    today = now.date()

    # Get existing record if any
    user_record = user_clock_log.get(phone)

    # If already clocked in today, block it
    if user_record and user_record.get("clock_in") and user_record["clock_in"].date() == today:
        clock_in_time = user_record["clock_in"].strftime("%I:%M %p")
        return ussd_response(f"END You already clocked in today at {clock_in_time}.")

    # Record new clock-in
    if not user_record:
        user_clock_log[phone] = {}

    user_clock_log[phone]["clock_in"] = now

    clock_in_time = now.strftime("%I:%M %p")
    expected_out_time = (now + timedelta(hours=8)).strftime("%I:%M %p")

    return ussd_response(
        f"END Clock-in recorded at {clock_in_time}.\n"
        f"Expected clock-out: {expected_out_time}."
    )

def clock_out(phone):
    now = datetime.now()
    clock_out_time = now.strftime("%I:%M %p")

    # Check if they clocked in first
    user_record = user_clock_log.get(phone)
    if not user_record or "clock_in" not in user_record:
        return ussd_response("END You haven't clocked in today. Clock in first.")

    # Save clock-out time
    user_clock_log[phone]["clock_out"] = now

    return ussd_response(f"END Clock-out recorded at {clock_out_time}.")

def ussd_response(text):
    return f"{text}"