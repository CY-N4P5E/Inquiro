"""
Inquiro - AI-Powered Document Research Assistant

Transform your documents into an intelligent knowledge base with local RAG technology.

This package provides a complete Retrieval-Augmented Generation (RAG) system that:
- Processes PDF documents with high-fidelity text extraction
- Creates semantic embeddings for intelligent search
- Provides natural language query interface
- Maintains complete source attribution
- Works entirely offline for privacy

Main modules:
- core: Core RAG functionality (document processing, embeddings, querying)
- ui: User interfaces (CLI, TUI, setup utilities)

Example usage:
    >>> from inquiro.core.query_data import query_documents
    >>> result = query_documents("What are the main findings?")
    >>> print(result)
"""

__version__ = "0.2.0"
__author__ = "Inquiro Team"
__email__ = "contact@inquiro.dev"
__license__ = "MIT"

# Import key functions for convenience
try:
    from core.query_data import query_documents
    from core.populate_database import build_knowledge_base
    from core.config import DATA_PATH, FAISS_PATH
    
    __all__ = [
        "query_documents",
        "build_knowledge_base", 
        "DATA_PATH",
        "FAISS_PATH",
    ]
except ImportError:
    # Handle case where dependencies might not be installed yet
    __all__ = []
