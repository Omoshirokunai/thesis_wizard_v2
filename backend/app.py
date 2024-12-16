import os

from flask import Flask, redirect, render_template, request, url_for
from history.history_manager import (
    add_model_response,
    add_user_input,
    calculate_content_statistics,
)
from llm_model import generate_response
from utils.model_loader import get_model, load_model
from utils.user_settings import load_settings, update_settings

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    response = None
    # if request.method == 'POST':
    #     prompt = request.form.get('prompt')
    #     if prompt:
    #         response = generate_response(prompt)
    # return render_template('index.html', response=response, settings=load_settings(), models=get_available_models())
    content_stats = {}

    if request.method == 'POST':
        prompt = request.form.get('prompt')
        if prompt:
            # Add the user prompt to history
            add_user_input(prompt)

            # Generate model response and log it
            response = generate_response(prompt)
            add_model_response(response)

            # Calculate content statistics
            content_stats = calculate_content_statistics()

    return render_template(
        'index.html',
        response=response,
        settings=load_settings(),
        stats=content_stats
    )



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
