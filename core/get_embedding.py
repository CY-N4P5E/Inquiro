"""
Provides a factory for creating a configured OllamaEmbeddings instance using the model from core.config.

Usage:
    from core.get_embedding import get_embedding
    embeddings = get_embedding()
    vectors = embeddings.embed_documents(["text1", "text2"])
    query_vec = embeddings.embed_query("query text")
"""

from langchain_ollama import OllamaEmbeddings
from core.config import OLLAMA_EMBEDDING_MODEL


def get_embedding():
    """
    Returns a configured OllamaEmbeddings instance using the model from core.config.
    """
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
    return embeddings
