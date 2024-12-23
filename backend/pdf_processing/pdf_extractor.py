import os

import pdfplumber


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

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Parameters:
    - pdf_path (str): Path to the PDF file.

    Returns:
    - str: Extracted text from the PDF.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return '\n'.join([page.extract_text() for page in pdf.pages if page.extract_text()])
    except Exception as e:
        print(f"Failed to extract text from {pdf_path}: {e}")
        return ""
