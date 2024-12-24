import json
import os

from pdftitle import get_title_from_file
from utils.constants import KNOWLEDGE_BASE_FILE


def get_pdf_title(file_path):
    """
    Extracts the title from a PDF file using the `pdftitle` library.

    Parameters:
    - file_path (str): Path to the PDF file.

    Returns:
    - str: Title of the PDF or its filename as fallback.
    """
    try:
        return get_title_from_file(file_path)
    except Exception:
        return os.path.basename(file_path)

def save_knowledge_base(data, output_file=KNOWLEDGE_BASE_FILE):
    """
    Saves extracted and chunked PDF data to a JSON file.

    Parameters:
    - data (dict): Data containing titles and text chunks.
    - output_file (str): Path to the JSON file for saving the knowledge base.
    """
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Knowledge base saved to {output_file}")
