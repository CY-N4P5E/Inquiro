"""
get_embedding.py
---------------
This module provides a centralized embedding function factory for the Inquiro RAG system.
It creates and configures OllamaEmbeddings instances using the configured embedding model.

Purpose:
This module serves as an abstraction layer for embedding generation, allowing easy 
configuration and potential swapping of embedding providers while maintaining a 
consistent interface throughout the system.

Features:
- Centralized embedding configuration
- Ollama embedding model integration
- Consistent interface for all embedding operations
- Configuration-driven model selection

Dependencies:
- langchain_ollama: For Ollama embeddings integration
- core.config: For centralized configuration management

Usage:
    from core.get_embedding import get_embedding
    
    embedding_function = get_embedding()
    embeddings = embedding_function.embed_documents(["text1", "text2"])
    query_embedding = embedding_function.embed_query("query text")

Functions:
    get_embedding(): Factory function that returns a configured OllamaEmbeddings instance

Configuration:
    Uses OLLAMA_EMBEDDING_MODEL from core.config for model selection.
    Default model: "nomic-embed-text"
    Can be overridden via OLLAMA_EMBEDDING_MODEL environment variable.

Return Type:
    OllamaEmbeddings: Configured embedding instance ready for text processing

Thread Safety:
    The returned embedding function is thread-safe and can be reused across 
    multiple operations and concurrent requests.

Author: Inquiro Development Team
Version: 2.0.0
"""

from langchain_ollama import OllamaEmbeddings
from core.config import OLLAMA_EMBEDDING_MODEL

def get_embedding():
    """
    Factory function that creates and returns a configured OllamaEmbeddings instance.
    
    This function serves as the primary interface for obtaining embedding functionality
    throughout the Inquiro system. It creates a new OllamaEmbeddings instance configured
    with the model specified in the system configuration.
    
    Returns:
        OllamaEmbeddings: A configured embedding instance that provides:
            - embed_documents(texts): Embed a list of documents
            - embed_query(text): Embed a single query text
            - Consistent vector dimensions for similarity operations
    
    Configuration:
        Uses OLLAMA_EMBEDDING_MODEL from core.config which defaults to "nomic-embed-text"
        and can be overridden via environment variable.
    
    Usage:
        >>> embedding_function = get_embedding()
        >>> query_vector = embedding_function.embed_query("sample query")
        >>> doc_vectors = embedding_function.embed_documents(["doc1", "doc2"])
    
    Notes:
        - Each call creates a new instance; consider caching for performance
        - The underlying Ollama service must be running and accessible
        - Model must be available in the local Ollama installation
        - Vector dimensions are consistent across all operations
    
    Raises:
        ConnectionError: If Ollama service is not accessible
        ModelNotFoundError: If the configured model is not available
    """
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
    return embeddings
