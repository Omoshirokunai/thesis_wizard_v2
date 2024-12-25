import os

import pdfplumber

from .chunking import chunk_text


def extract_pdfs_from_directory(directory):
    """
    Searches the given directory for PDF files.

    Parameters:
    - directory (str): Path to the directory to search.

    Returns:
    - list: A list of paths to PDF files.
    """
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return []

    pdf_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files


def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file.

    Parameters:
    - file_path (str): Path to the PDF file.

    Returns:
    - str: Extracted text from the PDF.
    """
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text
