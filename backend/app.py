import json
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
from rag.citation import format_citation, get_citation
from rag.retriever import OptimizedRetriever
from utils.constants import (
    DEFAULT_MODEL_PATH,
    DEFAULT_SETTINGS_FILE,
    HISTORY_FILE,
    KNOWLEDGE_BASE_FILE,
    SETTINGS_FILE,
)
from utils.model_download import check_and_download_default_model
from utils.model_loader import load_model
from utils.user_settings import load_settings, update_settings

app = Flask(__name__)
CORS(app) # Enable CORS for all routes
# Global state
pdf_files = []

pdf_info = {}
settings = load_settings()
model = load_model(settings["model_path"])
retriever = None

project_title = "Untitled Project"
section_context = "General Context"


def get_available_models():
    model_files = []
    for root, _, files in os.walk("models"):
        for file in files:
            if file.endswith(".gguf"):
                full_path = os.path.join(root, file)
                model_files.append(full_path)
    return model_files

class ProjectContext:
    def __init__(self):
        self.title = "Untitled Project"
        self.keywords = []
        self.section = "General"
        self.knowledge_base_updated = False

project_context = ProjectContext()

@app.route("/update_project", methods=["POST"])
def update_project():
    global project_context, retriever

    if "project_title" in request.form:
        project_context.title = request.form.get("project_title")
        # Search online when project title changes
        if retriever:
            # Update knowledge base based on title
            chunks = retriever.search(project_context.title)
            retriever.add_to_knowledge_base(chunks, f"title_{project_context.title}")
            project_context.knowledge_base_updated = True


    if "keywords" in request.form:
        new_keywords = request.form.get("keywords").split(',')
        project_context.keywords = [k.strip() for k in new_keywords if k.strip()]
        # Search online for each keyword
        if retriever:
            for keyword in project_context.keywords:
                retriever.add_to_knowledge_base(retriever.search(keyword), f"keyword_{keyword}")
            project_context.knowledge_base_updated = True

    if "section_context" in request.form:
        project_context.section = request.form.get("section_context")

    return redirect(url_for("index"))
@app.route("/api/autocomplete", methods=["POST"])
def api_autocomplete():
    """
    Endpoint for real-time autocomplete suggestions.
    Expects JSON input: {"prompt": "user text", "max_suggestions": 1}
    """
    pass

@app.route("/api/autocomplete", methods=["POST"])
def autocomplete():
    """
    Endpoint for real-time autocomplete suggestions for the flutter app"""
    query = request.json.get("current_text", "")
    max_suggestions = 1

    if not model:
        return jsonify({"suggestions": []})

    # Generate completion based on section context
    prompt = f"""In the {project_context.section} section of a paper about {project_context.title},
                complete the following text: {query}"""

    suggestions = model(prompt)
    return jsonify({"suggestions": suggestions})


@app.route("/", methods=["GET", "POST"])
def index():
    # global model
    global pdf_files, project_title, section_context, retriever

    response = None
    response = None
    content_stats = {}
    rag_results = []

    # content_stats = calculate_content_statistics()
    model_exists = os.path.exists(settings["model_path"])
    history = load_history()

    # if request.method == "POST" and request.form.get("prompt"):
    if request.method == "POST":

        if not model_exists:
            response = "No model loaded. Please select or download a model."
            content_stats = calculate_content_statistics()
            return render_template(
                "select_model.html",
                response=response,
                stats=content_stats,
                settings=settings,
                models=get_available_models(),
                model=model,
                model_exists=model_exists,
                pdf_info=pdf_info,
                history=history
            )

         # Handle query submission
        if "query" in request.form:
            query = request.form.get("query")
            add_user_input(query)

            # Get relevant context from knowledge base if available
            context = ""
            if retriever:
                relevant_chunks = retriever.search(query)
                rag_results = relevant_chunks[:3]  # Top 3 most relevant chunks
                context = "\n".join(chunk["text"] for chunk in rag_results)

            # Generate response with context
            prompt = f"""Project: {project_context.title}
                        Section: {project_context.section}
                        Context: {context}
                        Query: {query}"""


            response = model(prompt)
            response = response['choices'][0]['text'].strip()
            add_model_response(response)
            content_stats = calculate_content_statistics()

        elif "pdf_directory" in request.form:
            directory = request.form.get("pdf_directory")
            if os.path.exists(directory):
                # Initialize retriever only when we have PDFs
                retriever = OptimizedRetriever(
                    knowledge_base= KNOWLEDGE_BASE_FILE,
                    index_file="index.faiss"
                )

                pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
                knowledge_base = {}

                for pdf_file in pdf_files:
                    pdf_path = os.path.join(directory, pdf_file)
                    text = extract_text_from_pdf(pdf_path)
                    chunks = chunk_text(text)
                    title = get_pdf_title(pdf_file)
                    knowledge_base[title] = chunks
                    pdf_info[title] = {
                        "chunks": len(chunks),
                        "file_path": pdf_file
                    }

                save_knowledge_base(knowledge_base)
            else:
                # Handle invalid directory
                print(f"Directory does not exist: {directory}")



    return render_template(
        "index.html",
        response=response,
        stats=content_stats,
        project_context=project_context,
        history=history,
        pdf_files=pdf_files,
        rag_results=rag_results,
        pdf_info=pdf_info,
        models=get_available_models(),
        selected_model=settings["model_path"]
    )

@app.route("/download_model", methods=["POST"])
def download_model():
    # settings = load_settings()
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
        # settings = load_settings()
        model = load_model(settings["model_path"])
    except Exception as e:
        print(f"Error updating settings: {e}")

    return redirect(url_for("index"))

@app.route("/set_pdf_directory", methods=["POST"])
def set_pdf_directory():
    global pdf_files, pdf_info

    directory = request.form.get("pdf_directory")
    pdf_files = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.endswith(".pdf")
    ]

    # Extract and chunk PDFs
    chunked_data = {}
    pdf_info = {}  # Remove duplicate declaration

    for pdf_file in pdf_files:
        text = extract_text_from_pdf(pdf_file)
        chunks = chunk_text(text)
        title = get_pdf_title(pdf_file)
        chunked_data[title] = chunks

        # Store PDF info (remove duplicate block)
        pdf_info[title] = {
            "chunks": len(chunks),
            "file_path": pdf_file
        }

    save_knowledge_base(chunked_data)

    return redirect(url_for("index"))

@app.route("/get_citation", methods=["POST"])
def get_citation_route():
    file_path = request.form.get("file_path")
    manual = request.form.get("manual", "false") == "true"

    citation = get_citation(file_path, manual_input=manual)
    if citation:
        return jsonify({
            "success": True,
            "citation": format_citation(citation, "apa")
        })
    return jsonify({
        "success": False,
        "error": "Could not generate citation"
    })

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


if __name__ == "__main__":
    # settings = load_settings()
    # try:
    #     model = load_model(settings["model_path"])
    # except Exception as e:
    #     print(f"Error loading model: {e}")
    app.run(debug=True)