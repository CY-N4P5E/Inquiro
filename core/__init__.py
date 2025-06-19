"""
Inquiro Core Module
==================

The core module provides the fundamental functionality for the Inquiro RAG (Retrieval-Augmented 
Generation) system. This package contains all the essential components for document processing, 
embedding generation, vector database management, and query processing.

Modules:
--------
config.py:
    Central configuration management for the entire system including paths, models, 
    and processing parameters. Supports environment variable overrides and system validation.

get_embedding.py:
    Embedding function factory providing consistent access to Ollama embedding models.
    Abstracts embedding generation for use across the system.

populate_database.py:
    Document ingestion and vector database population. Handles PDF loading, text chunking,
    embedding generation, and FAISS index creation/updating with intelligent reset logic.

query_data.py:
    RAG query processing with configurable retrieval parameters. Provides command-line
    interface for querying the knowledge base with similarity filtering and verbose output.

Key Features:
------------
- Modular architecture with clear separation of concerns
- Centralized configuration with environment variable support
- Robust error handling and user feedback
- Configurable text processing and retrieval parameters
- Support for both reset and incremental database updates
- Thread-safe embedding operations
- Comprehensive logging and validation

Usage Examples:
--------------
# Setup system configuration
python -m core.config

# Populate database with documents
python -m core.populate_database

# Query the knowledge base
python -m core.query_data "What is machine learning?"

# Programmatic usage
from core import get_embedding, query_rag, populate_database
from core.config import validate_system

if validate_system():
    result = query_rag("your question", k=5, verbose=True)

Dependencies:
------------
- langchain_community: Vector stores and document loaders
- langchain_ollama: Ollama LLM and embedding integration  
- langchain_text_splitters: Document chunking utilities
- faiss: Vector similarity search
- PyMuPDF: PDF document processing

Author: Inquiro Development Team
Version: 2.0.0
License: See LICENSE file in project root
"""

# Core configuration and paths
from .config import (
    DATA_PATH, 
    FAISS_PATH, 
    INQUIRO_BASE_DIR,
    OLLAMA_QUERY_MODEL,
    OLLAMA_EMBEDDING_MODEL,
    DEFAULT_K,
    DEFAULT_SCORE_THRESHOLD,
    validate_system,
    get_config_summary
)

# Embedding functionality
from .get_embedding import get_embedding

# Database population functions
from .populate_database import (
    main as populate_database, 
    clear_database, 
    load_documents, 
    split_documents, 
    add_to_faiss,
    determine_reset_behavior
)

# Query processing
from .query_data import query_rag

# Public API
__all__ = [
    # Configuration
    'DATA_PATH',
    'FAISS_PATH', 
    'INQUIRO_BASE_DIR',
    'OLLAMA_QUERY_MODEL',
    'OLLAMA_EMBEDDING_MODEL',
    'DEFAULT_K',
    'DEFAULT_SCORE_THRESHOLD',
    'validate_system',
    'get_config_summary',
    
    # Embedding
    'get_embedding',
    
    # Database operations
    'populate_database',
    'clear_database',
    'load_documents',
    'split_documents',
    'add_to_faiss',
    'determine_reset_behavior',
    
    # Querying
    'query_rag'
]
