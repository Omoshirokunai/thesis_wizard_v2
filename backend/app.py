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
from utils.model_download import check_and_download_default_model
from utils.model_loader import load_model
from utils.user_settings import load_settings, update_settings

app = Flask(__name__)
CORS(app) # Enable CORS for all routes
# Global state
pdf_files = []
# model = None
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

        if not model:
            #TODO: replace with a no model loaded redirect to download model page insead
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
            # return render_template(
            #     "index.html",
            #     response=response,
            #     stats=content_stats,
            #     settings=settings,
            #     models=get_available_models(),
            #     model=model,
            #     model_exists=model_exists,
            #     pdf_info=pdf_info,
            #     history=history
            # )

        if "query" in request.form:
            query = request.form.get("query")
            add_user_input(query)

        # Check if we have a knowledge base and retriever
            if retriever and os.path.exists("knowledge_base.json"):
                try:
                    with open("knowledge_base.json", "r") as f:
                        kb_data = json.load(f)
                    if kb_data:  # Only do RAG if knowledge base has content
                        rag_results = retriever.retrieve_relevant_chunks(query, top_k=3)
                        rag_context = "\n".join([chunk["text"] for chunk in rag_results])
                        system_prompt = f"As a researcher working on '{project_title}', " \
                                    f"in the section '{section_context}', given the information: {rag_context} " \
                                    f"complete the sentence: {query}"
                    else:
                        system_prompt = f"As a researcher working on '{project_title}', " \
                                    f"in the section '{section_context}', " \
                                    f"complete the sentence: {query}"
                except (json.JSONDecodeError, FileNotFoundError):
                    system_prompt = f"As a researcher working on '{project_title}', " \
                                f"in the section '{section_context}', " \
                                f"complete the sentence: {query}"
            else:
                system_prompt = f"As a researcher working on '{project_title}', " \
                            f"in the section '{section_context}', " \
                            f"complete the sentence: {query}"

            response = model(system_prompt) if model else "No model loaded"
            add_model_response(response)
            content_stats = calculate_content_statistics()

        elif "pdf_directory" in request.form:
            directory = request.form.get("pdf_directory")
            if os.path.exists(directory):
                # Initialize retriever only when we have PDFs
                retriever = OptimizedRetriever(
                    knowledge_base="knowledge_base.json",
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


        elif "project_title" in request.form:
            project_title = request.form.get("project_title")
        elif "section_context" in request.form:
            section_context = request.form.get("section_context")
        # if not model:
        #     response = "No model loaded. Please select or download a model."
        # else:
        #     prompt = request.form.get("prompt")
        #     add_user_input(prompt)
        #     try:
        #         response = generate_response(prompt)
        #         add_model_response(response)
        #     except Exception as e:
        #         response = f"Error: {str(e)}"

    return render_template(
        "index.html",
         response=response,
        stats=content_stats,
        history=history,
        pdf_files=pdf_files,
        rag_results=rag_results,
        project_title=project_title,
        section_context=section_context,
        models=get_available_models(),
        selected_model=settings["model_path"]
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