
from langchain_ollama import OllamaEmbeddings


def get_embedding():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings
