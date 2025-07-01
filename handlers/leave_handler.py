from datetime import datetime

def handle_leave(inputs, phone, session):
    leave_types = {
        '1': 'Sick Leave',
        '2': 'Casual Leave',
        '3': 'Annual Leave'
    }

    if not inputs:
        return "CON Select Leave Type:\n1. Sick\n2. Casual\n3. Annual"

    # Step 1: Leave Type
    if len(inputs) == 1:
        choice = inputs[0]
        leave_name = leave_types.get(choice)
        if not leave_name:
            return "CON Invalid option. Choose:\n1. Sick\n2. Casual\n3. Annual"

        session['leave_type'] = leave_name
        return "CON Enter number of leave days:"

    # Step 2: Leave Days
    elif len(inputs) == 2:
        try:
            days = int(inputs[1])
            if days <= 0:
                return "CON Enter a valid number of days (1 or more):"
        except ValueError:
            return "CON Invalid number. Please enter a valid number of days:"

        session['leave_days'] = days
        return "CON Enter leave start date (DD-MM-YYYY):"

    # Step 3: Start Date
    elif len(inputs) == 3:
        start_date_str = inputs[2]

        try:
            start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        except ValueError:
            return "CON Invalid date format.\nUse DD-MM-YYYY (e.g. 01-07-2025):"

        leave_type = session.get('leave_type', 'Leave')
        days = session.get('leave_days', '?')
        formatted_start = start_date.strftime("%d %b %Y")

        return (
            f"END {leave_type} for {days} day(s) starting {formatted_start} "
            f"has been submitted.\n"
            f"Your office-in-charge will review and respond within 48hrs."
        )


    # Fallback
    return "END Error processing leave request. Please try again."
