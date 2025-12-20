"""
Provides a factory for creating a configured OllamaEmbeddings instance using the model from core.config.

Note: GPU acceleration for OLLAMA is configured at the Ollama server level, not handled by inquiro.
"""

from langchain_ollama import OllamaEmbeddings
from .config import OLLAMA_EMBEDDING_MODEL


def get_embedding():
    """
    Returns a embedding model based on the configurations
    """
    try:
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
        return embeddings
    except Exception as e:
        print(f"Error initializing embeddings: {e}")
        raise
