import os

from flask import Flask, redirect, render_template, request, url_for
from backend.utils.model_loader import load_model
from history.history_manager import (
    add_model_response,
    add_user_input,
    calculate_content_statistics,
    load_history,
)
from llm_model import generate_response
from pdf_processing.pdf_extractor import extract_pdfs_from_directory
from utils.user_settings import load_settings, update_settings

app = Flask(__name__)


# Global variable to hold PDF files
pdf_files = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global pdf_files
    response = None
    content_stats = {}

    if request.method == 'POST':
        prompt = request.form.get('prompt')
        if prompt:
            add_user_input(prompt)
            response = generate_response(prompt)
            add_model_response(response)
            content_stats = calculate_content_statistics()

    history = load_history()
    return render_template(
        'index.html',
        response=response,
        stats=content_stats,
        history=history,
        pdf_files=pdf_files
    )


@app.route('/set_pdf_directory', methods=['POST'])
def set_pdf_directory():
    global pdf_files
    directory = request.form.get('pdf_directory')
    pdf_files = extract_pdfs_from_directory(directory)
    return redirect(url_for('index'))


def get_available_models():
    model_files = []
    for root, _, files in os.walk("models"):
        for file in files:
            if file.endswith(".gguf"):
                full_path = os.path.join(root, file)
                model_files.append(full_path)
    return model_files


@app.route('/update_settings', methods=['POST'])
def update_settings_route():
    selected_model = request.form.get('model')
    system_prompt = request.form.get('system_prompt', '')

    try:
    # Update settings using utility function
        update_settings(model_path=selected_model, system_prompt=system_prompt)
    except Exception as e:
        print(f"Error updating settings: {e}")
    # Reload model based on updated settings
    load_model()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
