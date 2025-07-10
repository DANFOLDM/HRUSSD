from datetime import datetime, timedelta
import logging
import json
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('performance_reviews.log'),
        logging.StreamHandler()
    ]
)

# Performance database (would be DB in production)
performance_db = {
    "254743158232": {
        "last_review": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "rating": 4.5,
        "current_goals": [
            {"id": 1, "text": "Increase sales by 15%", "progress": 65, "due": "2025-09-30"},
            {"id": 2, "text": "Improve customer feedback scores", "progress": 40, "due": "2025-10-15"}
        ],
        "completed_training": [
            {"course": "Leadership 101", "date": "2025-05-15", "score": "A"},
            {"course": "Time Management", "date": "2025-06-22", "score": "B+"}
        ],
        "feedback_requests": []
    }
}

def ussd_response(text: str) -> str:
    """Format USSD response"""
    return text if text.startswith(('CON ', 'END ')) else f"CON {text}"

def _get_user_data(phone: str) -> Dict:
    """Get or create user performance record"""
    if phone not in performance_db:
        performance_db[phone] = {
            "last_review": "Not reviewed",
            "rating": "N/A",
            "current_goals": [{"id": 0, "text": "No current goals", "progress": 0, "due": "N/A"}],
            "completed_training": [{"course": "No training", "date": "N/A", "score": "N/A"}]
        }
    return performance_db[phone]

def _send_performance_report(phone: str, data: Dict) -> None:
    """Send detailed performance report via SMS"""
    from utils.sms_utils import SMSService
    sms_service = SMSService()
    report_message = (
        "PERFORMANCE REPORT\n"
        f"Rating: {data['rating']}/5\n"
        "Goals:\n" + "\n".join(f"- {g['text']} ({g['progress']}%)" for g in data['current_goals']) + "\n"
        "Upcoming Review: " + (datetime.strptime(data['last_review'], "%Y-%m-%d") + timedelta(days=90)).strftime("%d %b %Y")
    )
    sms_service.send([phone], report_message)
    logging.info(f"Performance Report Sent to {phone}")

def _submit_feedback_request(phone: str, comment: str) -> None:
    """Submit feedback to manager"""
    request = {
        "employee": phone,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "comment": comment,
        "status": "pending"
    }
    # In production, this would notify the manager
    logging.info(f"Feedback Request: {json.dumps(request)}")
    _get_user_data(phone)['feedback_requests'].append(request)


def _show_main_menu() -> str:
    """Display performance main menu"""
    menu = (
        "CON Performance Center:\n"
        "1. View My Ratings\n"
        "2. My Current Goals\n"
        "3. Training History\n"
        "4. Request Feedback\n"
        "0. Back"
    )
    return ussd_response(menu)

def _handle_view_rating(phone: str) -> str:
    """Display comprehensive rating information"""
    user_data = _get_user_data(phone)
    
    rating_info = (
        f"END Performance Rating:\n"
        f"Last Review: {user_data.get('last_review', 'N/A')}\n"
        f"Overall: {user_data.get('rating', 'N/A')}/5\n"
        f"Peer Avg: 4.2/5\n"
        f"Dept Rank: 12/45\n\n"
        "Detailed report sent via SMS"
    )
    
    # Send full report via SMS
    _send_performance_report(phone, user_data)
    
    return ussd_response(rating_info)

def _handle_view_goals(inputs: List[str], phone: str, session: Dict) -> Optional[str]:
    """Interactive goal tracking system"""
    user_data = _get_user_data(phone)
    goals_menu = ["CON Current Goals:"]
    
    for idx, goal in enumerate(user_data.get('current_goals', []), 1):
        progress_bar = "▓" * int(goal['progress']/10) + "░" * (10 - int(goal['progress']/10))
        goals_menu.append(
            f"{idx}. {goal['text']}\n"
            f"   {progress_bar} {goal['progress']}%\n"
            f"   Due: {goal['due']}"
        )
    
    goals_menu.append("0. Back")
    
    if not inputs:
        return ussd_response("\n".join(goals_menu))
    
    choice = inputs[0]
    if choice == '0':
        return None # Go back to main menu
    
    try:
        goal_idx = int(choice) - 1
        selected_goal = user_data['current_goals'][goal_idx]
        
        return ussd_response(
            f"CON Goal Details:\n"
            f"{selected_goal['text']}\n"
            f"Progress: {selected_goal['progress']}%\n"
            f"Due: {selected_goal['due']}\n\n"
            "1. Update Progress\n"
            "2. Request Help\n"
            "0. Back"
        )
    
    except (ValueError, IndexError):
        return ussd_response("CON Invalid selection. Try again:")

def _handle_view_training(phone: str) -> str:
    """Display training history with certifications"""
    user_data = _get_user_data(phone)
    training_history = ["END Completed Training:"]
    
    for course in user_data.get('completed_training', []):
        training_history.append(
            f"- {course['course']} ({course['date']})\n"
            f"  Grade: {course['score']}"
        )
    
    if not training_history:
        training_history.append("No training records found")
    
    return ussd_response("\n".join(training_history))

def _handle_request_feedback(inputs: List[str], phone: str, session: Dict) -> Optional[str]:
    """Feedback request workflow"""
    if not inputs:
        return ussd_response(
            "CON Request Feedback:\n"
            "Enter brief comment for your manager\n"
            "(Max 100 characters)\n"
            "0. Cancel"
        )
    
    choice = inputs[0]
    if choice == '0':
        return None # Go back to main menu
    
    feedback_text = choice[:100]  # Truncate to 100 chars
    _submit_feedback_request(phone, feedback_text)
    
    return ussd_response(
        "END Feedback request submitted.\n"
        "Your manager will respond within 48hrs.\n"
        "Reference #FB-" + phone[-6:]
    )

def handle_performance(inputs: List[str], phone: str, session: Dict) -> Optional[str]:
    """Handles the performance submenu."""
    stage = session.get('perf_stage', 'menu')

    if stage == 'menu':
        if not inputs:
            return _show_main_menu()
        
        choice = inputs[0]
        if choice == '0':
            return None  # Go back to main menu
        elif choice == '1':
            return _handle_view_rating(phone)
        elif choice == '2':
            session['perf_stage'] = 'goals_menu'
            return _handle_view_goals(inputs[1:], phone, session)
        elif choice == '3':
            return _handle_view_training(phone)
        elif choice == '4':
            session['perf_stage'] = 'feedback_menu'
            return _handle_request_feedback(inputs[1:], phone, session)
        else:
            return ussd_response("CON Invalid option. Please try again.")

    elif stage == 'goals_menu':
        response = _handle_view_goals(inputs, phone, session)
        if response is None:
            session['perf_stage'] = 'menu'
            return _show_main_menu()
        return response

    elif stage == 'feedback_menu':
        response = _handle_request_feedback(inputs, phone, session)
        if response is None:
            session['perf_stage'] = 'menu'
            return _show_main_menu()
        return response

    return ussd_response("END An unexpected error occurred in performance module.")
