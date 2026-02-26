import os
import faiss
import numpy as np
from crewai.tools import BaseTool
from langchain_community.document_loaders import PyPDFLoader
from openai import OpenAI


# OpenAI client for embeddings
client = OpenAI()


class FinancialDocumentTool(BaseTool):
    """
    Vector-based retrieval tool for financial PDF documents.

    Uses OpenAI embeddings and FAISS similarity search
    to return the most relevant document chunks.
    """

    name: str = "financial_document_reader"
    description: str = (
        "Performs vector-based retrieval on a financial PDF file. "
        "Requires two arguments: path (string) and query (string). "
        "Returns the most relevant document chunks."
    )

    def chunk_text(self, text: str, chunk_size: int = 2000, overlap: int = 200):
        """Split document text into overlapping chunks."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap

        return chunks

    def embed_text(self, text: str):
        """Generate embedding vector for input text."""
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(response.data[0].embedding, dtype="float32")

    def _run(self, path: str, query: str) -> str:
        """
        Retrieval pipeline:
        1. Load PDF
        2. Chunk text
        3. Embed chunks
        4. Build FAISS index
        5. Embed query
        6. Retrieve top-k similar chunks
        """
        try:
            if not path:
                return "No file path provided."

            if not os.path.exists(path):
                return f"File not found at path: {path}"

            if not query:
                return "No query provided for retrieval."

            # Load PDF
            loader = PyPDFLoader(path)
            docs = loader.load()

            full_text = ""
            for doc in docs:
                full_text += doc.page_content.strip() + "\n"

            if not full_text.strip():
                return "The document appears empty."

            # Chunk document
            chunks = self.chunk_text(full_text)
            if not chunks:
                return "No chunks generated from document."

            # Embed chunks
            chunk_embeddings = [
                self.embed_text(chunk)
                for chunk in chunks
            ]
            chunk_embeddings = np.vstack(chunk_embeddings)

            # Build FAISS index
            dimension = chunk_embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(chunk_embeddings)

            # Embed query
            query_embedding = self.embed_text(query).reshape(1, -1)

            # Retrieve most relevant chunks
            k = min(6, len(chunks))
            _, indices = index.search(query_embedding, k)

            relevant_chunks = [chunks[i] for i in indices[0]]

            return "\n\n".join(relevant_chunks)

        except Exception as e:
            return f"RAG error: {str(e)}"