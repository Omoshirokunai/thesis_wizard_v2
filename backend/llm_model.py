from utils.model_loader import load_model
from utils.user_settings import load_settings


def get_model():
    """Lazy load the model only when needed"""
    if not hasattr(get_model, "_model"):
        settings = load_settings()
        get_model._model = load_model(settings["model_path"])
    return get_model._model

def generate_response(prompt):
    # settings = load_settings()
    # model = load_model(settings["model_path"])
    try:
        model = get_model()
        if model is None:
            return "Model not loaded. Please select a model."
        settings = load_settings()
        system_prompt = settings.get("system_prompt", "")
        full_prompt = f"{system_prompt}\n\n{prompt}"


        response = model(full_prompt,
                         max_tokens=500,
                         temperature=0.3,
                         echo=False,
                         stream=False)
        return response['choices'][0]['text'].strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"
