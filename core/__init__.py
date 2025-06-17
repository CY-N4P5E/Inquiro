"""
Core module for Inquiro
Contains the main functionality for embedding, database operations, and querying.
"""

from .config import DATA_PATH, FAISS_PATH, INQUIRO_BASE_DIR
from .get_embedding import get_embedding
from .populate_database import main as populate_database, clear_database, load_documents, split_documents, add_to_faiss
from .query_data import query_rag

__all__ = [
    'DATA_PATH',
    'FAISS_PATH', 
    'INQUIRO_BASE_DIR',
    'get_embedding',
    'populate_database',
    'clear_database',
    'load_documents',
    'split_documents',
    'add_to_faiss',
    'query_rag'
]
