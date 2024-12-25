from utils.model_loader import load_model
from utils.user_settings import load_settings


def generate_response(prompt):
    settings = load_settings()
    model = load_model(settings["model_path"])
    if model is None:
        return "Model not loaded. Please select a model."

    # Combine the system prompt with the user's prompt
    # settings = load_settings()
    system_prompt = settings.get("system_prompt", "")
    full_prompt = f"{system_prompt}\n\n{prompt}"

    # Generate response
    try:
        response = model(full_prompt,
                         max_tokens=500,
                         temperature=0.2,
                         echo=False,
                         stream=False)
        return response['choices'][0]['text'].strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"
