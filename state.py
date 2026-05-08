import json
import os
import logging

STATE_FILE = "state.json"
logger = logging.getLogger(__name__)

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("State file is corrupted. Starting fresh.")
    return {"target_chat_id": None, "last_file_index": -1}

def save_state(state_data):
    with open(STATE_FILE, "w") as f:
        json.dump(state_data, f, indent=4)

def get_target_chat_id():
    return load_state().get("target_chat_id")

def set_target_chat_id(chat_id):
    state = load_state()
    state["target_chat_id"] = str(chat_id)
    save_state(state)

def get_last_file_index():
    return load_state().get("last_file_index", -1)

def set_last_file_index(index):
    state = load_state()
    state["last_file_index"] = int(index)
    save_state(state)
