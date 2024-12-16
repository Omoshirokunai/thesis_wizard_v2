import json

from genericpath import exists

SETTINGS_FILE = "usersettings.json"

def load_settings():
    """Loads user settings from the JSON file."""
    if not exists(SETTINGS_FILE):
        # Create usersettings.json and write default_settings.json into it
        with open("default_settings.json", "r") as default_f, open(SETTINGS_FILE, "w") as f:
            settings = json.load(default_f)
            json.dump(settings, f, indent=4)
            return settings

    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)
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
