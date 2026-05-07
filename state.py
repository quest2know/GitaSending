import json
import os

STATE_FILE = "state.json"

# State is now a dictionary of chat_id (str) -> user_data (dict)
# User data: {"alert_time": "08:00", "timezone": "Asia/Kolkata", "last_file_index": -1}

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def get_user(chat_id):
    state = load_state()
    chat_str = str(chat_id)
    if chat_str not in state:
        state[chat_str] = {
            "alert_time": "08:00",
            "timezone": "Asia/Kolkata",
            "last_file_index": -1
        }
        save_state(state)
    return state[chat_str]

def update_user(chat_id, **kwargs):
    state = load_state()
    chat_str = str(chat_id)
    if chat_str not in state:
        state[chat_str] = {
            "alert_time": "08:00",
            "timezone": "Asia/Kolkata",
            "last_file_index": -1
        }
    
    for key, value in kwargs.items():
        state[chat_str][key] = value
        
    save_state(state)

def get_all_users():
    return load_state()
