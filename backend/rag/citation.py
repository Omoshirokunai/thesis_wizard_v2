# citation.py
import os
from dataclasses import dataclass
from typing import Dict, Optional

import PyPDF2
import requests


@dataclass
class Citation:
    title: str
    authors: list[str]
    year: str
    doi: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None

def extract_pdf_metadata(file_path: str) -> Optional[Dict]:
    """Extract metadata from PDF file."""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            metadata = reader.metadata
            if metadata:
                return {k.lower(): v for k, v in metadata.items()}
    except Exception as e:
        print(f"Error extracting metadata: {e}")
    return None

def search_crossref(title: str) -> Optional[Dict]:
    """Search CrossRef API for citation metadata."""
    try:
        url = f"https://api.crossref.org/works"
        params = {
            "query": title,
            "rows": 1
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["message"]["items"]:
                return data["message"]["items"][0]
    except Exception as e:
        print(f"Error searching CrossRef: {e}")
    return None

def format_citation(citation: Citation, style: str = "apa") -> str:
    """Format citation in specified style."""
    if style == "apa":
        authors = ", ".join(citation.authors[:-1])
        if len(citation.authors) > 1:
            authors += f", & {citation.authors[-1]}"
        elif citation.authors:
            authors = citation.authors[0]

        citation_text = f"{authors} ({citation.year}). {citation.title}"
        if citation.journal:
            citation_text += f". {citation.journal}"
            if citation.volume:
                citation_text += f", {citation.volume}"
                if citation.issue:
                    citation_text += f"({citation.issue})"
        if citation.doi:
            citation_text += f". https://doi.org/{citation.doi}"
        return citation_text

    # Add other citation styles as needed
    return ""

def get_citation(file_path: str, manual_input: bool = False) -> Optional[Citation]:
    """Get citation for a PDF file."""
    if manual_input:
        # Get citation details from user input
        print("Enter citation details:")
        title = input("Title: ")
        authors = input("Authors (comma-separated): ").split(",")
        year = input("Year: ")
        journal = input("Journal (optional): ")
        doi = input("DOI (optional): ")

        return Citation(
            title=title.strip(),
            authors=[a.strip() for a in authors],
            year=year.strip(),
            journal=journal.strip() if journal else None,
            doi=doi.strip() if doi else None
        )

    # Try extracting from PDF metadata
    metadata = extract_pdf_metadata(file_path)
    if metadata and metadata.get('title'):
        # Convert PDF metadata to Citation object
        return Citation(
            title=metadata.get('title', ''),
            authors=metadata.get('author', '').split(',') if metadata.get('author') else [],
            year=metadata.get('creationdate', '')[:4],
            doi=metadata.get('doi')
        )

    # If metadata extraction fails, try online search
    filename = os.path.basename(file_path)
    title = os.path.splitext(filename)[0]
    crossref_data = search_crossref(title)

    if crossref_data:
        return Citation(
            title=crossref_data.get('title', [title])[0],
            authors=[author.get('family', '') + ', ' + author.get('given', '')
                    for author in crossref_data.get('author', [])],
            year=str(crossref_data.get('published-print', {}).get('date-parts', [['']])[0][0]),
            doi=crossref_data.get('DOI'),
            journal=crossref_data.get('container-title', [None])[0],
            volume=crossref_data.get('volume'),
            issue=crossref_data.get('issue')
        )

    return None

# Example usage:
if __name__ == "__main__":
    file_path = "example.pdf"

    # Try automatic citation
    citation = get_citation(file_path)
    if citation:
        print("Automatic citation found:")
        print(format_citation(citation, "apa"))
    else:
        print("No automatic citation found")

    # Manual citation option
    manual_citation = get_citation(file_path, manual_input=True)
    if manual_citation:
        print("\nManual citation:")
        print(format_citation(manual_citation, "apa"))