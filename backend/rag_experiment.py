import json
import os

from pdf_processing.chunking import chunk_text
from pdf_processing.pdf_extractor import extract_text_from_pdf
from rag.retriever import OptimizedRetriever

# Paths and directories
PDF_DIRECTORY = "D:/0000_masters_thesis/DHF/01_Project_Overview"
KNOWLEDGE_BASE_PATH = "knowledge_base.json"
INDEX_PATH = "index.faiss"

# Step 1: Extract text from PDFs
def build_knowledge_base():
    knowledge_base = {}

    for pdf_file in os.listdir(PDF_DIRECTORY):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(PDF_DIRECTORY, pdf_file)
            print(f"Processing: {pdf_file}")

            # Extract text
            text = extract_text_from_pdf(pdf_path)

            # Chunk text
            chunks = chunk_text(text, chunk_size=300)

            # Save chunks in the knowledge base
            knowledge_base[pdf_file] = chunks

    # Save to JSON
    with open(KNOWLEDGE_BASE_PATH, "w") as f:
        json.dump(knowledge_base, f, indent=4)

    print(f"Knowledge base saved to {KNOWLEDGE_BASE_PATH}")

# Step 2: Test Retrieval
def test_retrieval():
    retriever = OptimizedRetriever(
        knowledge_base=KNOWLEDGE_BASE_PATH,
        index_file=INDEX_PATH
    )

    print("Testing Retrieval...\n")
    while True:
        query = input("Enter a query (or type 'exit' to quit): ").strip()
        if query.lower() == 'exit':
            break

        # Retrieve relevant chunks
        results = retriever.retrieve_relevant_chunks(query, top_k=3)

        print("\nTop Results:")
        for i, result in enumerate(results):
            print(f"\nResult {i + 1}")
            print(f"Text: {result['text']}")
            print(f"Metadata: {result['metadata']}")
            print(f"Similarity: {result['similarity']:.4f}")
        print("\n" + "-" * 40)

# Main Function
if __name__ == "__main__":
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        print("Building knowledge base...")
        build_knowledge_base()
    test_retrieval()
