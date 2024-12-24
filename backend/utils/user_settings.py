import json
import os

from genericpath import exists
from utils.constants import DEFAULT_SETTINGS_FILE, SETTINGS_FILE

# SETTINGS_FILE = "usersettings.json"

def load_settings():
    """Load user settings from JSON file"""
    try:
        if not os.path.exists(SETTINGS_FILE):
            # Copy default settings
            with open(DEFAULT_SETTINGS_FILE, "r") as default_f:
                settings = json.load(default_f)
                os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
                with open(SETTINGS_FILE, "w") as f:
                    json.dump(settings, f, indent=4)
                return settings

        with open(SETTINGS_FILE, "r") as f:
            content = f.read()
            if not content.strip():
                # File exists but empty
                raise FileNotFoundError
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
         # On any error, reset to defaults
        with open(DEFAULT_SETTINGS_FILE, "r") as default_f:
            settings = json.load(default_f)
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)
            return settings

def update_settings(model_path=None, system_prompt=None):
    """
    Updates the settings in usersettings.json.

    Parameters:
    - model_path (str): Path to the selected model file.
    - system_prompt (str): System prompt to use.
    """
    settings = load_settings()
    if model_path is not None:
        settings["model_path"] = model_path
    if system_prompt is not None:
        settings["system_prompt"] = system_prompt

    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
    print("Settings updated.")
