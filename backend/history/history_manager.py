import json

# File to persist history for user and model content
HISTORY_FILE = "history.json"

def initialize_history():
    """Initializes the history file with an empty structure."""
    history = {"user_content": [], "model_content": []}
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def load_history():
    """Loads the history from the JSON file."""
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        initialize_history()
        history = {"user_content": [], "model_content": []}
    return history

def save_history(history):
    """Saves the history to the JSON file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def add_user_input(user_input):
    """Adds user input to the history."""
    history = load_history()
    history["user_content"].append(user_input)
    save_history(history)

def add_model_response(model_response):
    """Adds model response to the history."""
    history = load_history()
    history["model_content"].append(model_response)
    save_history(history)

def calculate_content_statistics():
    """
    Calculates the percentage of words contributed by the user
    vs. the model in the entire history.

    Returns:
    - dict: A dictionary with counts and percentages.
    """
    history = load_history()
    user_word_count = sum(len(content.split()) for content in history["user_content"])
    model_word_count = sum(len(content.split()) for content in history["model_content"])
    total_word_count = user_word_count + model_word_count

    if total_word_count == 0:
        return {"user_percentage": 0, "model_percentage": 0}

    return {
        "user_words": user_word_count,
        "model_words": model_word_count,
        "user_percentage": (user_word_count / total_word_count) * 100,
        "model_percentage": (model_word_count / total_word_count) * 100,
    }
