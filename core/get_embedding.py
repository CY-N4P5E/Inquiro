"""
get_embedding.py

This module provides a function to instantiate and return an OllamaEmbeddings object

Functions:
    get_embedding(): Returns an OllamaEmbeddings instance for embedding text.

Models:
    embeddings: OllamaEmbeddings instance configured with the 'nomic-embed-text' model.
"""

from langchain_ollama import OllamaEmbeddings


def get_embedding():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings
