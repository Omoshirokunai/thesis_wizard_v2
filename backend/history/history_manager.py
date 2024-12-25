
import json
import os
from datetime import datetime
from difflib import SequenceMatcher

from utils.constants import HISTORY_FILE
from utils.user_settings import load_settings


def initialize_history():
    """Initializes the history file with an empty structure."""
    history = {
        "completions": [] # list of gpt completions
        }

    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
    return history

def load_history():
    """Load or initialize history"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                content = f.read()
                if not content.strip():
                    return initialize_history()
                return json.loads(content)
                # history = json.loads(content)
                # if not all(k in history for k in ["user_input", "model_content"]):
                #     return initialize_history()
                # return history

        return initialize_history()
    except (json.JSONDecodeError, FileNotFoundError):
        return initialize_history()

def save_history(history):
    """
    Saves conversation history to a file.

    Parameters:
    - history (dict): History dictionary to save.
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def add_unique_sentence(content_list, new_entry):
    """
    Manages content list by keeping only most recent duplicate entries.
    Returns: (bool) True if added as new, False if replaced duplicate
    """
    new_content = new_entry.get('content') if isinstance(new_entry, dict) else new_entry
    duplicate_index = None

    # Check for duplicates
    for i, entry in enumerate(content_list):
        existing_content = entry.get('content') if isinstance(entry, dict) else entry
        similarity = SequenceMatcher(None, str(existing_content), str(new_content)).ratio()
        if similarity > 0.9:
            duplicate_index = i
            break

    # Handle duplicate found
    if duplicate_index is not None:
        content_list.pop(duplicate_index)  # Remove old duplicate
        content_list.append(new_entry)     # Add new entry
        return False

    # No duplicate - add new entry
    content_list.append(new_entry)
    return True

def add_user_input(input_text):
    """Add user input, replacing duplicates with most recent"""
    try:
        history = load_history()
        if "completions" not in history:
            history["completions"] = []

        entry = {
            "timestamp": datetime.now().isoformat(),
            "content": input_text,
            "type": "user"
        }

        add_unique_sentence(history["completions"], entry)
        save_history(history)
        return True
    except Exception as e:
        print(f"Error adding user input: {e}")
        return False

def add_model_response(response_text):
    """Add model response, replacing duplicates with most recent"""
    try:
        history = load_history()
        settings = load_settings()

        text = response_text.get('choices', [{}])[0].get('text', '') if isinstance(response_text, dict) else str(response_text)

        entry = {
            "type": "model",
            "content": text,
            "timestamp": datetime.now().isoformat(),
            "model": {
                "path": settings.get("model_path", ""),
                "name": os.path.basename(settings.get("model_path", "")),
                "system_prompt": settings.get("system_prompt", "")
            }
        }

        add_unique_sentence(history.get("completions", []), entry)
        save_history(history)
        return True
    except Exception as e:
        print(f"Error adding model response: {e}")
        return False

def calculate_content_statistics():
    """
    Calculates content statistics from completion history.
    """
    history = load_history()
    completions = history.get("completions", [])

    # Filter messages by type
    user_messages = [entry for entry in completions if entry["type"] == "user"]
    model_messages = [entry for entry in completions if entry["type"] == "model"]

    # Calculate word counts using 'content' field
    user_words = sum(len(entry["content"].split()) for entry in user_messages)
    model_words = sum(len(entry["content"].split()) for entry in model_messages)
    total = user_words + model_words

    return {
        "user_words": user_words,
        "model_words": model_words,
        "user_percentage": round((user_words / total * 100) if total > 0 else 0, 2),
        "model_percentage": round((model_words / total * 100) if total > 0 else 0, 2),
        "total_exchanges": len(completions) // 2
    }
# def calculate_content_statistics():
#     """
#     Calculates content statistics from completion history.
#     """
#     history = load_history()
#     completions = history.get("completions", [])

#     user_messages = [entry for entry in completions if entry["type"] == "user"]
#     model_messages = [entry for entry in completions if entry["type"] == "model"]

#     user_words = sum(len(entry["user_input"].split()) for entry in user_messages)
#     model_words = sum(len(entry["content"].split()) for entry in model_messages)
#     total = user_words + model_words
#     # user_words = sum(len(text.split()) for text in history["user_input"])
#     # print(history["model_content"])
#     # model_words = sum(len(text.split()) for text in history["model_content"])
#     # total = user_words + model_words

#     return {
#         "user_words": user_words,
#         "model_words": model_words,
#         "user_percentage": round((user_words / total * 100) if total > 0 else 0, 2),
#         "model_percentage": round((model_words / total * 100) if total > 0 else 0, 2),
#         "total_exchanges": len(completions) // 2
#     }

