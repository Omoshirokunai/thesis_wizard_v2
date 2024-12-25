
import json
import os

#     return {
#         "user_words": user_word_count,
#         "model_words": model_word_count,
#         "user_percentage": (user_word_count / total_word_count) * 100,
#         "model_percentage": (model_word_count / total_word_count) * 100,
#     }
from datetime import datetime

from utils.constants import HISTORY_FILE
from utils.user_settings import load_settings

# HISTORY_FILE = "history.json"

def initialize_history():
    """Initializes the history file with an empty structure."""
    # history = {
    #     "user_input": [],
    #     "model_content": []

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

def add_user_input(input_text):
    """
    Adds a user input to the history.

    Parameters:
    - input_text (str): User input text.
    """
    history = load_history()
    time_stamp = datetime.now().isoformat()

    entry = {"time_stamp": time_stamp,
             "user_input": input_text,
             "type": "user"}
    if "completions" not in history:
        history["completions"] = []
    history["completions"].append(entry)

    save_history(history)


def add_model_response(response_text):
    """
    Adds a model response to the history.

    Parameters:
    - response_text (str): Model response text.
    """

    # Ensure we're storing the text content, not the dict
    history = load_history()
    timestamp = datetime.now().isoformat()
    settings = load_settings()

    if isinstance(response_text, dict):
        # text = response_text.get('choices', [{}])[0].get('text', '')
        text = response_text.get('choices', [{}])[0].get('text', '')
    else:
        text = str(response_text)

    entry = {
        "type": "model",
        "content": text,
        "timestamp": timestamp,
        "model": {
            "path": settings.get("model_path", ""),
            "name": os.path.basename(settings.get("model_path", "")),
            "system_prompt": settings.get("system_prompt", "")
        }
    }
    if "completions" not in history:
        history["completions"] = []
    history["completions"].append(entry)
    timestamp = datetime.now().isoformat()
    settings = load_settings()

    save_history(history)

def calculate_content_statistics():
    """
    Calculates content statistics from completion history.
    """
    history = load_history()
    completions = history.get("completions", [])

    user_messages = [entry for entry in completions if entry["type"] == "user"]
    model_messages = [entry for entry in completions if entry["type"] == "model"]

    user_words = sum(len(entry["user_input"].split()) for entry in user_messages)
    model_words = sum(len(entry["content"].split()) for entry in model_messages)
    total = user_words + model_words
    # user_words = sum(len(text.split()) for text in history["user_input"])
    # print(history["model_content"])
    # model_words = sum(len(text.split()) for text in history["model_content"])
    # total = user_words + model_words

    return {
        "user_words": user_words,
        "model_words": model_words,
        "user_percentage": round((user_words / total * 100) if total > 0 else 0, 2),
        "model_percentage": round((model_words / total * 100) if total > 0 else 0, 2),
        "total_exchanges": len(completions) // 2
    }

