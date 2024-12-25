import os

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_cors import CORS
from history.history_manager import (
    add_model_response,
    add_user_input,
    calculate_content_statistics,
    load_history,
)
from llm_model import generate_response
from pdf_processing.chunking import chunk_text
from pdf_processing.metadata import get_pdf_title, save_knowledge_base
from pdf_processing.pdf_extractor import extract_text_from_pdf
from utils.model_download import check_and_download_default_model
from utils.model_loader import load_model
from utils.user_settings import load_settings, update_settings

app = Flask(__name__)

# Global state
pdf_files = []
model = None
pdf_info = {}

# @app.route("/", methods=["GET", "POST"])
# def index():
#     global model, pdf_files

#     response = None
#     content_stats = {}
#     settings = load_settings()

#      # Check if model file exists
#     model_exists = os.path.exists(settings["model_path"])

#     if request.method == "POST":
#         prompt = request.form.get("prompt")
#         system_prompt = settings.get("system_prompt", "")
#         if prompt:
#             if not model:
#                 response = "No model loaded. Please select or download a model."
#             else:
#                 add_user_input(prompt)
#                 try:
#                     response = generate_response(prompt)
#                     add_model_response(response)
#                 except Exception as e:
#                     response = f"An error occurred: {e}"
#                 content_stats = calculate_content_statistics()

#     history = load_history()
#     models = get_available_models()

#     return render_template(
#          "index.html",
#         response=response,
#         stats=content_stats,
#         history=history,
#         settings=settings,
#         models=models,
#         model=model,
#         model_exists=model_exists,
#         pdf_info=pdf_info
#     )
@app.route("/", methods=["GET", "POST"])
def index():
    global model

    response = None
    content_stats = calculate_content_statistics()
    settings = load_settings()
    model_exists = os.path.exists(settings["model_path"])

    if request.method == "POST" and request.form.get("prompt"):
        if not model:
            response = "No model loaded. Please select or download a model."
        else:
            prompt = request.form.get("prompt")
            add_user_input(prompt)
            try:
                response = generate_response(prompt)
                add_model_response(response)
            except Exception as e:
                response = f"Error: {str(e)}"

    return render_template(
        "index.html",
        response=response,
        stats=content_stats,
        settings=settings,
        models=get_available_models(),
        model=model,
        model_exists=model_exists,
        pdf_info=pdf_info
    )
@app.route("/autocomplete", methods=["POST"])
def autocomplete():
    """
    Endpoint for real-time autocomplete suggestions.
    Expects JSON input: {"prompt": "user text", "max_suggestions": 1}
    """
    pass


@app.route("/download_model", methods=["POST"])
def download_model():
    settings = load_settings()
    default_model_name = settings["model_path"].split("/")[-1]
    models_dir = "models"

    try:
        model_path = check_and_download_default_model(models_dir, default_model_name)
        update_settings(model_path=model_path)
        return redirect(url_for("index"))
    except Exception as e:
        print(f"Error downloading model: {e}")
        return redirect(url_for("index"))

@app.route("/update_settings", methods=["POST"])
def update_settings_route():
    global model

    selected_model = request.form.get("model")
    system_prompt = request.form.get("system_prompt", "")

    try:
        update_settings(model_path=selected_model, system_prompt=system_prompt)
        settings = load_settings()
        model = load_model(settings["model_path"])
    except Exception as e:
        print(f"Error updating settings: {e}")

    return redirect(url_for("index"))

@app.route("/set_pdf_directory", methods=["POST"])
def set_pdf_directory():
    global pdf_files, pdf_info
    global pdf_files, pdf_info

    directory = request.form.get("pdf_directory")
    pdf_files = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.endswith(".pdf")
    ]

    # Extract and chunk PDFs
    chunked_data = {}
    pdf_info = {}

    pdf_info = {}

    for pdf_file in pdf_files:
        text = extract_text_from_pdf(pdf_file)
        chunks = chunk_text(text)
        title = get_pdf_title(pdf_file)
        chunked_data[title] = chunks

        # Store PDF info
        pdf_info[title] = {
            "chunks": len(chunks),
            "file_path": pdf_file
        }

        # Store PDF info
        pdf_info[title] = {
            "chunks": len(chunks),
            "file_path": pdf_file
        }

    save_knowledge_base(chunked_data)

    return redirect(url_for("index"))

@app.route("/api/status", methods=["GET"])
def get_status():
    """
    Endpoint to check backend status and loaded resources
    """
    return jsonify({
        "success": True,
        "model_loaded": model is not None,
        "pdfs_loaded": len(pdf_info) > 0,
        "pdf_count": len(pdf_info),
        "model_info": {
            "name": os.path.basename(load_settings().get("model_path", "")),
            "system_prompt": load_settings().get("system_prompt", "")
        }
    })
def get_available_models():
    model_files = []
    for root, _, files in os.walk("models"):
        for file in files:
            if file.endswith(".gguf"):
                full_path = os.path.join(root, file)
                model_files.append(full_path)
    return model_files

if __name__ == "__main__":
    settings = load_settings()
    try:
        model = load_model(settings["model_path"])
    except Exception as e:
        print(f"Error loading model: {e}")
    app.run(debug=True)
