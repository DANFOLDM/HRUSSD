from datetime import datetime, timedelta

_sessions = {}

def get_user_session(session_id):
    return _sessions.get(session_id, {})

def update_user_session(session_id, session_data):
    _sessions[session_id] = session_data

def clear_user_session(session_id):
    if session_id in _sessions:
        del _sessions[session_id]

def cleanup_old_sessions():
    """Removes sessions older than 1 hour to prevent memory leaks."""
    now = datetime.now()
    old_sessions = []
    for session_id, session_data in _sessions.items():
        last_activity = session_data.get('last_activity', now)
        if now - last_activity > timedelta(hours=1):
            old_sessions.append(session_id)
    
    for session_id in old_sessions:
        clear_user_session(session_id)
