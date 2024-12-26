import json
import os

import faiss
import numpy as np
from rag.search_online import search_arxiv, search_springer
from sentence_transformers import SentenceTransformer
from utils.constants import KNOWLEDGE_BASE_FILE


class OptimizedRetriever:
    def __init__(self, model_name="all-MiniLM-L6-v2", knowledge_base=KNOWLEDGE_BASE_FILE, index_file="index.faiss"):
        """
        Initializes the optimized retriever with FAISS for fast similarity search.

        Parameters:
        - model_name (str): Name of the SentenceTransformer model for embeddings.
        - knowledge_base (str): Path to the knowledge base JSON file.
        - index_file (str): Path to the FAISS index file.
        """
        self.model = SentenceTransformer(model_name)
        self.knowledge_base = knowledge_base
        self.index_file = index_file
        self.text_chunks = []
        self.metadata = []
        self.index = None

        #  # Create empty knowledge base if not exists
        if not os.path.exists(self.knowledge_base):
            with open(self.knowledge_base, 'w') as f:
                json.dump({}, f)
            print(f"Created empty knowledge base at {self.knowledge_base}")

        # self.load_knowledge_base()
        # self.load_or_create_index()
    def load_or_initialize_knowledge_base(self):
        """Initialize or load existing knowledge base"""
        try:
            with open(self.knowledge_base, "r") as f:
                data = json.load(f)

            if not data:  # Empty knowledge base
                return False

            self.load_knowledge_base()
            self.load_or_create_index()
            return True

        except (json.JSONDecodeError, FileNotFoundError):
            with open(self.knowledge_base, "w") as f:
                json.dump({}, f)
            return False

    def load_knowledge_base(self):
        """
        Loads the knowledge base and extracts text chunks and metadata.
        """

        try:
            with open(self.knowledge_base, "r") as f:
                data = json.load(f)

            self.text_chunks = []
            self.metadata = []

            for title, chunks in data.items():
                for chunk in chunks:
                    self.text_chunks.append(chunk)
                    self.metadata.append({"title": title})

            print(f"Loaded {len(self.text_chunks)} chunks from knowledge base")

        except json.JSONDecodeError:
            print("Error reading knowledge base, creating empty one")
            with open(self.knowledge_base, 'w') as f:
                json.dump({}, f)

    def load_or_create_index(self):
        """
        Loads or creates a FAISS index for efficient similarity search.
        """
        dimension = self.model.get_sentence_embedding_dimension()

        # If index file exists, load it
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
            print(f"Loaded FAISS index from {self.index_file}")
        else:
            # Create a new FAISS index
            self.index = faiss.IndexFlatL2(dimension)
            print("Created a new FAISS index.")

            # Compute embeddings for all chunks and add to the index
            embeddings = self.model.encode(self.text_chunks, convert_to_numpy=True)
            self.index.add(embeddings)

            # Save the index for future use
            faiss.write_index(self.index, self.index_file)
            print(f"Saved FAISS index to {self.index_file}")

    def update_knowledge_base(self, query: str) -> bool:
        """Update knowledge base with new information from online sources"""
        try:
            # Search online sources
            arxiv_chunks, arxiv_citations = search_arxiv(query, max_results=3)
            springer_chunks, springer_citations = search_springer(query, max_results=3)

            # Load existing knowledge base
            with open(self.knowledge_base, 'r') as f:
                kb_data = json.load(f)

            # Add new content
            updated = False
            for chunk, citation in zip(arxiv_chunks, arxiv_citations):
                key = f"arxiv_{citation.title}"
                if key not in kb_data:
                    kb_data[key] = {
                        "text": chunk,
                        "metadata": {
                            "source": "arxiv",
                            "title": citation.title,
                            "authors": citation.authors,
                            "year": citation.year,
                            "url": citation.url
                        }
                    }
                    self.text_chunks.append(chunk)
                    self.metadata.append({"title": citation.title, "source": "arxiv"})
                    updated = True

            # Update FAISS index if new content was added
            if updated:
                new_embeddings = self.model.encode([chunk["text"] for chunk in kb_data.values()
                                                  if chunk not in self.text_chunks],
                                                  convert_to_numpy=True)
                if len(new_embeddings) > 0:
                    self.index.add(new_embeddings)
                    faiss.write_index(self.index, self.index_file)

                # Save updated knowledge base
                with open(self.knowledge_base, 'w') as f:
                    json.dump(kb_data, f, indent=2)

            return updated
        except Exception as e:
            print(f"Error updating knowledge base: {e}")
            return False

    def retrieve_relevant_chunks(self, query, top_k=3):
        """
        Retrieves the top-k most relevant chunks for a query using FAISS.

        Parameters:
        - query (str): The user's query or input.
        - top_k (int): Number of top chunks to return.

        Returns:
        - list: List of dictionaries containing text, metadata, and similarity scores.
        """
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k * 2)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or i >= top_k:  # Take only top_k results
                continue

            similarity = 1 / (1 + distances[0][i])
            if similarity < 0.3:  # Filter out low similarity results
                continue

            results.append({
                "text": self.text_chunks[idx],
                "metadata": self.metadata[idx],
                "similarity": similarity  # Convert L2 to similarity
            })

        # return results
        return sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_k]


