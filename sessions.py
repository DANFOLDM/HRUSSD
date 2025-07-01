_sessions = {}

def get_user_session(session_id):
    return _sessions.get(session_id, {})

def update_user_session(session_id, session_data):
    _sessions[session_id] = session_data
def clear_user_session(session_id):
    if session_id in _sessions:
        del _sessions[session_id]
