import llama_cpp

from .user_settings import load_settings

# Global variables to hold the model instance and path
model = None
current_model_path = None

def load_model():
    """
    Loads or reloads the model based on the model path in usersettings.json.

    Returns:
    - model: An instance of the loaded model.
    """
    global model, current_model_path
    settings = load_settings()
    model_path = settings.get("model_path")

    if model_path and model_path != current_model_path:
        print(f"Loading model from: {model_path}")
        model = llama_cpp.Llama(model_path=model_path)
        current_model_path = model_path
    return model

def get_model():
    """
    Returns the current model instance, loading it if necessary.

    Returns:
    - model: An instance of the loaded model or None if not loaded.
    """
    if model is None:
        load_model()
    return model
