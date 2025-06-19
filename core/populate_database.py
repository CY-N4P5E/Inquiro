"""
populate_database.py
-------------------
This module loads PDF documents from the data directory, splits them into text chunks, 
generates embeddings, and stores them in a FAISS vector database for efficient retrieval. 
It provides modular reset/update functionality for database management.

Features:
- Intelligent database reset/update logic with user interaction
- PDF document loading with PyMuPDF integration
- Configurable text chunking with overlap
- FAISS vector store creation and merging
- Unique chunk ID generation for traceability
- Error handling and user feedback
- Modular command-line interface

Dependencies:
- langchain_community: For PDF loading and FAISS integration
- langchain_text_splitters: For document chunking
- core.get_embedding: For embedding generation
- core.config: For centralized configuration

CLI Usage:
    python populate_database.py --reset           # Reset database
    python populate_database.py --no-reset        # Update database
    python populate_database.py                   # Interactive mode

Database Operations:
- Reset Mode: Clears existing database and rebuilds from scratch
- Update Mode: Adds new documents to existing database
- Interactive Mode: Prompts user for preferred operation

Functions:
    main(): Entry point with modular reset behavior and user interaction
    determine_reset_behavior(): Handles flag logic and user prompts
    prompt_user_for_reset(): Interactive user input for database operation
    load_documents(): Loads PDF files from configured data directory
    split_documents(): Splits documents using configurable chunking parameters
    add_to_faiss(): Creates or updates FAISS vector store with embeddings
    calculate_chunk_ids(): Generates unique identifiers for document chunks
    clear_database(): Safely removes existing FAISS index

Configuration:
    All configuration imported from core.config:
    - DATA_PATH: Directory containing PDF documents
    - FAISS_PATH: Vector database storage location
    - CHUNK_SIZE: Size of text chunks for processing
    - CHUNK_OVERLAP: Overlap between consecutive chunks

Author: Inquiro Development Team
Version: 2.0.0
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
from core.config import CHUNK_SIZE, CHUNK_OVERLAP

def main():
    """
    Entry point for the script. Handles command-line arguments for resetting the database,
    loads documents, splits them into chunks, and adds them to the FAISS vector store.
    
    The reset behavior:
    - If --reset flag is provided, clears the database before adding documents
    - If --no-reset flag is provided, explicitly updates without resetting
    - If no flag is provided, prompts user for their preference
    """
    parser = argparse.ArgumentParser(description="Populate the FAISS vector database with PDF documents.")
    parser.add_argument("--reset", action="store_true", help="Reset the database before adding documents.")
    parser.add_argument("--no-reset", action="store_true", help="Update the database without resetting.")
    args = parser.parse_args()
    
    # Determine reset behavior based on flags or user input
    should_reset = determine_reset_behavior(args.reset, args.no_reset)
    
    if should_reset:
        print("✨ Clearing Database")
        clear_database()

    documents = load_documents()
    chunks = split_documents(documents)
    add_to_faiss(chunks)


def determine_reset_behavior(reset_flag, no_reset_flag):
    """
    Determines whether to reset the database based on command-line flags or user input.
    
    Args:
        reset_flag (bool): True if --reset flag was provided
        no_reset_flag (bool): True if --no-reset flag was provided
    
    Returns:
        bool: True if database should be reset, False if it should be updated
    
    Raises:
        SystemExit: If both conflicting flags are provided
    """
    # Check for conflicting flags
    if reset_flag and no_reset_flag:
        print("Error: Cannot specify both --reset and --no-reset flags.")
        exit(1)
    
    # If reset flag is explicitly set, follow it
    if reset_flag:
        return True
    
    # If no-reset flag is explicitly set, follow it
    if no_reset_flag:
        return False
    
    # If no flag is provided, ask the user
    return prompt_user_for_reset()


def prompt_user_for_reset():
    """
    Prompts the user to decide whether to reset or update the database.
    
    Returns:
        bool: True if user wants to reset, False if user wants to update
    """
    while True:
        print("\nDatabase operation mode:")
        print("1. Reset database (clear existing data and rebuild)")
        print("2. Update database (add new documents to existing data)")
        
        choice = input("Choose an option (1/2) or (r/u): ").lower().strip()
        
        if choice in ['1', 'r', 'reset']:
            return True
        elif choice in ['2', 'u', 'update']:
            return False
        else:
            print("Invalid choice. Please enter 1, 2, r, or u.")


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
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
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
