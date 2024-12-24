# import json

# # File to persist history for user and model content
# HISTORY_FILE = "history.json"

# def initialize_history():
#     """Initializes the history file with an empty structure."""
#     history = {"user_content": [], "model_content": []}
#     with open(HISTORY_FILE, "w") as f:
#         json.dump(history, f, indent=4)

# def load_history():
#     """Loads the history from the JSON file."""
#     try:
#         with open(HISTORY_FILE, "r") as f:
#             history = json.load(f)
#     except FileNotFoundError:
#         initialize_history()
#         history = {"user_content": [], "model_content": []}
#     return history

# def save_history(history):
#     """Saves the history to the JSON file."""
#     with open(HISTORY_FILE, "w") as f:
#         json.dump(history, f, indent=4)

# def add_user_input(user_input):
#     """Adds user input to the history."""
#     history = load_history()
#     history["user_content"].append(user_input)
#     save_history(history)

# def add_model_response(model_response):
#     """Adds model response to the history."""
#     history = load_history()
#     history["model_content"].append(model_response)
#     save_history(history)

# def calculate_content_statistics():
#     """
#     Calculates the percentage of words contributed by the user
#     vs. the model in the entire history.

#     Returns:
#     - dict: A dictionary with counts and percentages.
#     """
#     history = load_history()
#     user_word_count = sum(len(content.split()) for content in history["user_content"])
#     model_word_count = sum(len(content.split()) for content in history["model_content"])
#     total_word_count = user_word_count + model_word_count

#     if total_word_count == 0:
#         return {"user_percentage": 0, "model_percentage": 0}

#     return {
#         "user_words": user_word_count,
#         "model_words": model_word_count,
#         "user_percentage": (user_word_count / total_word_count) * 100,
#         "model_percentage": (model_word_count / total_word_count) * 100,
#     }
import json
import os

from utils.constants import HISTORY_FILE

# HISTORY_FILE = "history.json"

def initialize_history():
    """Initializes the history file with an empty structure."""
    history = {
        "user_input": [],
        "model_content": []
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
                history = json.loads(content)
                if not all(k in history for k in ["user_input", "model_content"]):
                    return initialize_history()
                return history
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
    if input_text not in history["user_input"]:  # Ensure uniqueness
        history["user_input"].append(input_text)
    save_history(history)

def add_model_response(response_text):
    """
    Adds a model response to the history.

    Parameters:
    - response_text (str): Model response text.
    """
    history = load_history()
    if response_text not in history["model_content"]:
        history["model_content"].append(response_text)
    save_history(history)

def calculate_content_statistics():
    """
    Calculates content statistics (user vs. model contributions).

    Returns:
    - dict: Statistics including word counts and percentages.
    """
    history = load_history()
    user_words = sum(len(text.split()) for text in history["user_input"])
    model_words = sum(len(text.split()) for text in history["model_content"])
    total = user_words + model_words

    return {
        "user_words": user_words,
        "model_words": model_words,
        "user_percentage": (user_words / total * 100) if total > 0 else 0,
        "model_percentage": (model_words / total * 100) if total > 0 else 0
    }
