import os

from flask import Flask, redirect, render_template, request, url_for
from history.history_manager import (
    add_model_response,
    add_user_input,
    calculate_content_statistics,
    load_history,
)
from pdf_processing.chunking import chunk_text
from pdf_processing.metadata import get_pdf_title, save_knowledge_base
from pdf_processing.pdf_extractor import extract_text_from_pdf
from utils.model_loader import load_model
from utils.user_settings import load_settings, update_settings

app = Flask(__name__)

# Global state
pdf_files = []
model = None

@app.route("/", methods=["GET", "POST"])
def index():
    global model

    response = None
    content_stats = {}

    if request.method == "POST":
        prompt = request.form.get("prompt")
        if prompt:
            add_user_input(prompt)
            response = model(prompt) if model else "" ##! TODO: add code to check if model gives no output
            add_model_response(response)
            content_stats = calculate_content_statistics()

    history = load_history()
    settings = load_settings()
    models = get_available_models()

    return render_template(
        "index.html",
        response=response,
        stats=content_stats,
        history=history,
        settings=settings,
        models=models,
    )

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
    global pdf_files

    directory = request.form.get("pdf_directory")
    pdf_files = [
        os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".pdf")
    ]

    # Extract and chunk PDFs
    chunked_data = {}
    for pdf_file in pdf_files:
        text = extract_text_from_pdf(pdf_file)
        chunks = chunk_text(text)
        title = get_pdf_title(pdf_file)
        chunked_data[title] = chunks

    save_knowledge_base(chunked_data)

    return redirect(url_for("index"))

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
