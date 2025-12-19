"""
Provides a factory for creating a configured OllamaEmbeddings instance using the model from core.config.

Features:
- Configurable model selection from environment variables or config
- Error handling and validation

Usage:
    from core.get_embedding import get_embedding
    embeddings = get_embedding()
    vectors = embeddings.embed_documents(["text1", "text2"])
    query_vec = embeddings.embed_query("query text")
    
Configuration:
    - OLLAMA_EMBEDDING_MODEL: Model name from config.py
    
Dependencies:
    - langchain_ollama: For OllamaEmbeddings
    - core.config: For centralized configuration
    
Note: GPU acceleration is configured at the Ollama server level, not in the client code.

author: ADPer
version: 2.0.0
"""

from langchain_ollama import OllamaEmbeddings
from core.config import OLLAMA_EMBEDDING_MODEL


def get_embedding():
    """
    Returns a configured OllamaEmbeddings instance using the model from core.config.
    
    GPU usage is configured at the Ollama server level when starting the Ollama service,
    not through the LangChain client.
    """
    try:
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
        return embeddings
    except Exception as e:
        print(f"Error initializing embeddings: {e}")
        raise
