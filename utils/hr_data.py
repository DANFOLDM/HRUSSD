from datetime import datetime, timedelta

def clock_in(phone):
    now = datetime.now()
    clock_in_time = now.strftime("%I:%M %p")  # e.g., 09:45 AM
    expected_out = (now + timedelta(hours=8)).strftime("%I:%M %p")

    return (
        f"Clock-in recorded for {phone} at {clock_in_time}.\n"
        f"Expected clock-out time is {expected_out}."
    )

def clock_out(phone):
    now = datetime.now()
    clock_out_time = now.strftime("%I:%M %p")
    return f"Clock-out recorded for {phone} at {clock_out_time}."
