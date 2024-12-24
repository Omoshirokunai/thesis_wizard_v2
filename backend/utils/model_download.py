import os

from huggingface_hub import hf_hub_download


def download_model(repo_id="bartowski/Nemotron-Mini-4B-Instruct-GGUF", model_file="my_model.gguf", cache_dir="models"):
    """
    Downloads a model file from Hugging Face and saves it locally.

    Parameters:
    - repo_id (str): The repository ID on Hugging Face (e.g., 'bartowski/Nemotron-Mini-4B-Instruct-GGUF').
    - model_file (str): The specific file within the repository to download (e.g., 'Nemotron-Mini-4B-Instruct-Q6_K.gguf').
    - cache_dir (str): The directory where the model file will be stored.

    Returns:
    - str: Path to the downloaded model file.
    """
    model_path = hf_hub_download(repo_id=repo_id, filename=model_file, cache_dir=cache_dir)
    print(f"Model downloaded to: {model_path}")
    return model_path

def check_and_download_default_model(models_dir, default_model_name):
    """
    Checks if the default model exists; if not, downloads it using `download_model`.

    Parameters:
    - models_dir (str): Directory where models are stored.
    - default_model_name (str): Name of the default model to check or download.

    Returns:
    - str: Path to the default model file.
    """
    model_path = os.path.join(models_dir, default_model_name)
    if not os.path.exists(model_path):
        print(f"Default model '{default_model_name}' not found. Downloading...")
        os.makedirs(models_dir, exist_ok=True)
        # Use your provided download_model function
        repo_id = "bartowski/Nemotron-Mini-4B-Instruct-GGUF"
        model_file = default_model_name
        model_path = download_model(repo_id=repo_id, model_file=model_file, cache_dir=models_dir)
    else:
        print("Default model already exists.")
    return model_path