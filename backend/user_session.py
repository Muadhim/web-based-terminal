active_sessions = {}

def add_session(token, ws):
    if token in active_sessions:
        return False
    active_sessions[token] = ws
    return True

def remove_session(token):
    if token in active_sessions:
        del active_sessions[token]

def is_valid_token(token):
    return token == "YWRtaW46cGFzc3dvcmQ="  # base64(admin:password)
