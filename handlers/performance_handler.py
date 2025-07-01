from datetime import datetime, timedelta

# Simulated performance database
performance_db = {
    "default": {
        "punctuality": 85,
        "task_completion": 90,
        "attendance": 95,
        "last_review": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
        "feedback": "Meets expectations",
        "improvement_areas": ["Time management", "Technical skills"],
        "recent_achievements": ["Completed project X", "Received client praise"]
    }
}

def handle_performance(inputs, phone, session):
    level = len(inputs)
    user_perf = performance_db.get(phone, performance_db["default"])
    
    # Main menu
    if level == 0:
        session['stage'] = 'perf_main'
        return ussd_response(
            "CON Performance Dashboard\n"
            "1. Current Summary\n"
            "2. Improvement Areas\n"
            "3. Recent Achievements\n"
            "4. Compare to Team\n"
            "5. Set Goals"
        )
    
    # Current summary
    elif level == 1 and inputs[0] == '1':
        return ussd_response(
            f"END Current Performance ({datetime.now().strftime('%b %Y')})\n"
            f"Punctuality: {user_perf['punctuality']}%\n"
            f"Tasks Completed: {user_perf['task_completion']}%\n"
            f"Attendance: {user_perf['attendance']}%\n"
            f"Last Review: {user_perf['last_review']}\n"
            f"Feedback: {user_perf['feedback']}"
        )
    
    # Improvement areas
    elif level == 1 and inputs[0] == '2':
        areas = "\n".join([f"{i+1}. {area}" for i, area in enumerate(user_perf['improvement_areas'])])
        return ussd_response(
            f"CON Improvement Areas\n{areas}\n\n"
            "1. Get Resources\n"
            "2. Request Training\n"
            "0. Back"
        )
    
    # Recent achievements
    elif level == 1 and inputs[0] == '3':
        achievements = "\n".join([f"✓ {ach}" for ach in user_perf['recent_achievements']])
        return ussd_response(f"END Recent Achievements:\n{achievements}")
    
    # Team comparison
    elif level == 1 and inputs[0] == '4':
        return ussd_response(
            "END Team Comparison:\n"
            "Punctuality: Top 40%\n"
            "Productivity: Top 30%\n"
            "Engagement: Average"
        )
    
    # Goal setting
    elif level == 1 and inputs[0] == '5':
        session['stage'] = 'set_goal'
        return ussd_response(
            "CON Set Performance Goal\n"
            "1. Punctuality\n"
            "2. Task Completion\n"
            "3. Skill Development\n"
            "0. Back"
        )
    
    # Handle submenus
    elif session.get('stage') == 'set_goal':
        if inputs[-1] == '1':
            return ussd_response("CON Enter target punctuality % (Current: {user_perf['punctuality']}%)")
        elif inputs[-1] == '2':
            return ussd_response("CON Enter target completion % (Current: {user_perf['task_completion']}%)")
        elif inputs[-1] == '3':
            return ussd_response("CON Enter skill to develop:")
        elif inputs[-1] == '0':
            return handle_performance([], phone, session)
    
    return ussd_response("END Invalid selection. Try again.")

def ussd_response(text):
    return f"{text}"