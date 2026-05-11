import json
import os
import logging

STATE_FILE = "state.json"
logger = logging.getLogger(__name__)

def load_state():
    """Loads the state from state.json. Returns a default structure if file is missing/broken."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                # Migration: Ensure new structure exists if old one was used
                if "chat_ids" not in data:
                    data["chat_ids"] = []
                    if "target_chat_id" in data and data["target_chat_id"]:
                        data["chat_ids"].append(data["target_chat_id"])
                return data
        except json.JSONDecodeError:
            logger.error("State file is corrupted. Starting fresh.")
            
    return {"chat_ids": [], "last_file_index": -1}

def save_state(state_data):
    """Saves the state_data to state.json."""
    with open(STATE_FILE, "w") as f:
        json.dump(state_data, f, indent=4)

def get_chat_ids():
    """Returns a list of all registered chat IDs."""
    return load_state().get("chat_ids", [])

def add_chat_id(chat_id):
    """Adds a new chat ID to the list if it doesn't already exist."""
    state = load_state()
    chat_id_str = str(chat_id)
    if chat_id_str not in state["chat_ids"]:
        state["chat_ids"].append(chat_id_str)
        save_state(state)
        return True
    return False

def get_last_file_index():
    """Returns the index of the last file sent globally."""
    return load_state().get("last_file_index", -1)

def set_last_file_index(index):
    """Updates the global last file index."""
    state = load_state()
    state["last_file_index"] = int(index)
    save_state(state)

# Keep these for backward compatibility if needed, but they refer to the first ID in the list
def get_target_chat_id():
    ids = get_chat_ids()
    return ids[0] if ids else None

def set_target_chat_id(chat_id):
    add_chat_id(chat_id)
