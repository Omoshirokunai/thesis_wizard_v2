from utils.model_loader import get_model
from utils.user_settings import load_settings


def generate_response(prompt):
    model = get_model()
    if model is None:
        return "Model not loaded. Please select a model."

    # Combine the system prompt with the user's prompt
    settings = load_settings()
    system_prompt = settings.get("system_prompt", "")
    full_prompt = f"{system_prompt}\n\n{prompt}"

    # Generate response
    response = model(full_prompt, max_tokens=100, temperature=0.7)
    return response['choices'][0]['text']
