import os

from llama_cpp import Llama

from .constants import DEFAULT_MODEL_PATH
from .user_settings import load_settings


def load_model(model_path=DEFAULT_MODEL_PATH):
    """
    Load the LLM model. If no path is provided, fallback to the default model from user settings.

    Parameters:
    - model_path (str): Path to the model file (e.g., ".gguf").

    Returns:
    - Llama: Loaded model object.
    """
    if not model_path or not os.path.exists(model_path):
        raise ValueError("Model path is invalid or missing.")

    print(f"Loading model from: {model_path}")
    return Llama(model_path=model_path,n_ctx=256,
            n_batch=32,
            n_threads=2,
            verbose=False)