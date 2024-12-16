# download_model.py
# from huggingface_hub import hf_hub_download

# # Path to download model files
# model_dir = "./backend/models/Nemotron-Mini-4B-Instruct"

# # Download specific model file
# hf_hub_download(
#     repo_id="bartowski/Nemotron-Mini-4B-Instruct-GGUF",
#     filename="Nemotron-Mini-4B-Instruct-Q6_K.gguf",
#     local_dir=model_dir,
#     local_files_only=False
# )

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
