"""
populate_database.py
-------------------
This script loads PDF documents from the data directory, splits them into text chunks, generates embeddings, and stores them in a FAISS vector database for efficient retrieval. It can also reset (clear) the database if requested.

Main Functions:
- main(): Entry point for CLI usage. Handles argument parsing and orchestrates the pipeline.
- load_documents(): Loads all PDF files from the data directory using PyMuPDFLoader.
- split_documents(): Splits loaded documents into smaller chunks for embedding.
- add_to_faiss(): Adds document chunks to a FAISS vector store, creating or updating the index as needed.
- calculate_chunk_ids(): Assigns unique IDs to each chunk based on source and page.
- clear_database(): Deletes the FAISS index directory to reset the database.
"""

import argparse
import os
from pathlib import Path
import shutil
import glob
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from core.get_embedding import get_embedding
from langchain_community.vectorstores import FAISS

from core.config import DATA_PATH, FAISS_PATH

def main():
    """
    Entry point for the script. Handles command-line arguments for resetting the database,
    loads documents, splits them into chunks, and adds them to the FAISS vector store.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    documents = load_documents()
    chunks = split_documents(documents)
    add_to_faiss(chunks)


def load_documents():
    """
    Loads all PDF files from the data directory specified by DATA_PATH.
    Uses PyMuPDFLoader to extract pages from each PDF as Document objects.
    Returns a list of Document objects (pages).
    """
    documents = []
    pdf_files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {DATA_PATH} directory.")
        return documents
    
    for pdf_file in pdf_files:
        print(f"Loading {pdf_file}...")
        loader = PyMuPDFLoader(pdf_file)
        documents.extend(loader.load())
    
    print(f"Loaded {len(documents)} pages from {len(pdf_files)} PDF files.")
    return documents


def split_documents(documents: list[Document]):
    """
    Splits a list of Document objects into smaller text chunks using RecursiveCharacterTextSplitter.
    Returns a list of chunked Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")
    return chunks


def add_to_faiss(chunks: list[Document]):
    """
    Adds a list of chunked Document objects to the FAISS vector store.
    Loads an existing FAISS index if present, or creates a new one.
    Embeddings are generated using the embedding function from get_embedding().
    """
    if not chunks:
        print("No chunks to add to database.")
        return

    chunks_with_ids = calculate_chunk_ids(chunks)

    embedding_function = get_embedding()

    if os.path.exists(FAISS_PATH):
        print("Loading existing FAISS index...")
        try:
            db = FAISS.load_local(FAISS_PATH, embedding_function, allow_dangerous_deserialization=True)
            
            print("Adding new documents to existing index...")
            
            new_db = FAISS.from_documents(chunks_with_ids, embedding_function)
            
            db.merge_from(new_db)
            
        except Exception as e:
            print(f"Error loading existing index: {e}")
            print("Creating new FAISS index...")
            db = FAISS.from_documents(chunks_with_ids, embedding_function)
    else:
        print("Creating new FAISS index...")
        db = FAISS.from_documents(chunks_with_ids, embedding_function)

    # Save the index
    db.save_local(FAISS_PATH)
    print(f"✅ Saved FAISS index with {len(chunks_with_ids)} chunks.")


def calculate_chunk_ids(chunks):
    """
    Assigns a unique ID to each chunk based on its source file and page number.
    The ID format is: <source>:<page>:<chunk_index>
    Modifies the metadata of each chunk in-place.
    Returns the list of chunks with updated IDs.
    """
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    """
    Deletes the FAISS index directory specified by FAISS_PATH if it exists.
    Used to reset the vector database.
    """
    if os.path.exists(FAISS_PATH):
        shutil.rmtree(FAISS_PATH)
        print("Database cleared.")


if __name__ == "__main__":
    # Run the main function if the script is executed directly
    main()
