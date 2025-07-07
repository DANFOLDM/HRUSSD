from datetime import datetime, timedelta

# Simulated performance data
performance_data = {
    "254743158232": {
        "last_review": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "rating": "4.5",
        "goals": ["Increase sales", "Improve customer feedback"],
        "completed_training": ["Leadership 101", "Time Management"]
    },
    "254798765432": {
        "last_review": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
        "rating": "3.8",
        "goals": ["Reduce errors", "Learn new software"],
        "completed_training": ["Excel Advanced"]
    }
}

def handle_performance(inputs, phone, session):
    try:
        level = len(inputs)
        
        # Initialize session if needed
        if 'stage' not in session:
            session['stage'] = 'performance_main'
        
        # Main Menu
        if level == 0 or session.get('stage') == 'performance_main':
            session['stage'] = 'performance_main'
            return ussd_response(
                "CON Performance Summary:\n"
                "1. View Ratings\n"
                "2. Current Goals\n"
                "3. Training History\n"
                "0. Main Menu"
            )
        
        # Option Handling
        choice = inputs[0]
        
        if choice == '0':
            return ussd_response("END Returning to main menu")
        
        # Create user record if doesn't exist
        if phone not in performance_data:
            performance_data[phone] = {
                "last_review": "Not reviewed",
                "rating": "Not rated",
                "goals": ["No current goals"],
                "completed_training": ["No training completed"]
            }
        
        user_data = performance_data[phone]
        
        if choice == '1':
            return ussd_response(
                f"END Performance Rating:\n"
                f"Last Review: {user_data['last_review']}\n"
                f"Rating: {user_data['rating']}/5"
            )
        
        elif choice == '2':
            goals_text = "\n".join(f"- {goal}" for goal in user_data['goals'])
            return ussd_response(
                f"END Current Goals:\n"
                f"{goals_text}"
            )
        
        elif choice == '3':
            training_text = "\n".join(f"- {course}" for course in user_data['completed_training'])
            return ussd_response(
                f"END Completed Training:\n"
                f"{training_text}"
            )
        
        return ussd_response("END Invalid option selected")
    
    except Exception as e:
        print(f"Performance Error: {str(e)}")
        return ussd_response("END System error. Please try again.")

def ussd_response(text):
    return text