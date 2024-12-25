import json
import os

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class OptimizedRetriever:
    def __init__(self, model_name="all-MiniLM-L6-v2", knowledge_base="knowledge_base.json", index_file="index.faiss"):
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

        self.load_knowledge_base()
        self.load_or_create_index()

    def load_knowledge_base(self):
        """
        Loads the knowledge base and extracts text chunks and metadata.
        """
        if not os.path.exists(self.knowledge_base):
            raise FileNotFoundError(f"Knowledge base '{self.knowledge_base}' not found.")

        with open(self.knowledge_base, "r") as f:
            data = json.load(f)

        for title, chunks in data.items():
            for chunk in chunks:
                self.text_chunks.append(chunk)
                self.metadata.append({"title": title})

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
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:  # No result found
                continue
            results.append({
                "text": self.text_chunks[idx],
                "metadata": self.metadata[idx],
                "similarity": 1 / (1 + distances[0][i])  # Convert L2 to similarity
            })

        return results
