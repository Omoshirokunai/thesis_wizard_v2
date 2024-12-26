#search online (arxiv, wikipedia, etc.) for relevant text chunks add to knowledge base
#include citations
import os
from typing import List, Tuple

import arxiv
import requests
from dotenv import load_dotenv
from rag.citation import Citation
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()
spinger_api_key = os.getenv("SPRINGER_API_KEY")

# SPRINGER_CALLS = 100
# SPRINGER_PERIOD = 3600  # 1 hour
@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=4, max=10))
@sleep_and_retry
@limits(calls=1000, period=3600)
def search_springer(query: str, max_results: int = 7) -> Tuple[List[str], List[Citation]]:
    """Search Springer Nature API for relevant papers."""
    try:
        url = "https://api.springernature.com/metadata/json"
        params = {
            "q": query,
            "api_key": spinger_api_key,
            "s": max_results,
            "p": 1
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        text_chunks = []
        citations = []

        for record in data.get("records", []):
            # Extract abstract if available
            abstract = record.get("abstract", "")
            if abstract:
                text_chunks.append(abstract)

                # Create citation
                citation = Citation(
                    title=record.get("title", ""),
                    authors=[a.get("name", "") for a in record.get("authors", [])],
                    year=record.get("publicationDate", "")[:4],
                    doi=record.get("doi", ""),
                    journal=record.get("publicationName", ""),
                    volume=record.get("volume", ""),
                    issue=record.get("number", ""),
                    publisher="Springer Nature"
                )
                citations.append(citation)

        return text_chunks, citations

    except requests.exceptions.RequestException as e:
        if e.response and e.response.status_code == 429:
            print("Rate limit reached for Springer API")
            raise
        print(f"Error searching Springer: {e}")
        return [], []

@retry(stop=stop_after_attempt(3),
         wait=wait_exponential(multiplier=1, min=4, max=10))
@sleep_and_retry
@limits(calls=100, period=3600)
def search_arxiv(query: str, max_results: int = 7) -> Tuple[List[str], List[Citation]]:
    """Search ArXiv with rate limiting."""
    try:
        search = arxiv.Search(query=query, max_results=max_results)
        results = list(search.results())

        text_chunks = []
        citations = []

        for result in results:
            text_chunks.append(result.summary)
            citation = Citation(
                title=result.title,
                authors=[str(author) for author in result.authors],
                year=str(result.published.year),
                doi=result.doi,
                journal="arXiv",
                url=result.entry_id
            )
            citations.append(citation)

        return text_chunks, citations

    except Exception as e:
        print(f"Error searching arXiv: {e}")
        return [], []