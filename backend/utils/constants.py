import os

# Get base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Define paths relative to base directory
# Create user_profile directory if it doesn't exist
USER_PROFILE_DIR = os.path.join(BASE_DIR, "user_profile")
os.makedirs(USER_PROFILE_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(USER_PROFILE_DIR, "user_settings.json")
DEFAULT_SETTINGS_FILE = os.path.join(USER_PROFILE_DIR, "default_settings.json")
HISTORY_FILE = os.path.join(USER_PROFILE_DIR, "history.json")
KNOWLEDGE_BASE_FILE = os.path.join(USER_PROFILE_DIR, "knowledge_base.json")

# Default model path
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "models", "Nemotron-Mini-4B-Instruct-GGUF.gguf")