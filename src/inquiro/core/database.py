"""
populate_database.py
-------------------
This module loads PDF, DOCX, and DOC documents from the data directory, splits them into text chunks, 
generates embeddings, and stores them in a FAISS vector database for efficient retrieval. 
It provides modular reset/update functionality for database management.

Features:
- Intelligent database reset/update logic with user interaction
- PDF, DOCX, and DOC document loading with PyMuPDF and Unstructured integration
- Configurable text chunking with overlap
- FAISS vector store creation and merging
- Unique chunk ID generation for traceability
- Error handling and user feedback
- Modular command-line interface

Dependencies:
- langchain_community: For PDF, DOCX, and DOC loading and FAISS integration
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
    load_documents(): Loads PDF, DOCX, and DOC files from configured data directory
    split_documents(): Splits documents using configurable chunking parameters
    add_to_faiss(): Creates or updates FAISS vector store with embeddings
    calculate_chunk_ids(): Generates unique identifiers for document chunks
    clear_database(): Safely removes existing FAISS index

Configuration:
    All configuration imported from core.config:
    - DATA_PATH: Directory containing PDF, DOCX, and DOC documents
    - FAISS_PATH: Vector database storage location
    - CHUNK_SIZE: Size of text chunks for processing
    - CHUNK_OVERLAP: Overlap between consecutive chunks

Author: ADPer
Version: 2.0.0
"""

import argparse
import os
from pathlib import Path
import shutil
import glob
from langchain_community.document_loaders import PyMuPDFLoader
try:
    from langchain_community.document_loaders import UnstructuredWordDocumentLoader
    from langchain_community.document_loaders import UnstructuredFileLoader
except ImportError:
    # Fallback for older versions or missing unstructured dependency
    UnstructuredWordDocumentLoader = None
    UnstructuredFileLoader = None
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from .embedding import get_embedding
from .config import DATA_PATH, FAISS_PATH
from .config import CHUNK_SIZE, CHUNK_OVERLAP
from .config import DEFAULT_MEMORY_LIMIT

def main():
    """
    Entry point for the script. Handles command-line arguments for resetting the database,
    loads documents, splits them into chunks, and adds them to the FAISS vector store.
    
    The reset behavior:
    - If --reset flag is provided, clears the database before adding documents
    - If --no-reset flag is provided, explicitly updates without resetting
    - If no flag is provided, prompts user for their preference
    
    Memory optimization:
    - Process documents in batches to reduce memory usage
    - Use batch_size parameter to control memory consumption
    - Use memory_limit to prevent memory overload (in MB)
    - --optimized-memory flag uses the batch processing approach
    - --traditional flag uses the original non-batched approach
    """
    parser = argparse.ArgumentParser(description="Populate the FAISS vector database with PDF, DOCX, and DOC documents.")
    parser.add_argument("--reset", action="store_true", help="Reset the database before adding documents.")
    parser.add_argument("--no-reset", action="store_true", help="Update the database without resetting.")
    parser.add_argument("--batch-size", type=int, default=1000, 
                        help="Number of chunks to process at once (default: 1000)")
    parser.add_argument("--memory-limit", type=int, default=DEFAULT_MEMORY_LIMIT,
                        help="Memory limit in MB (0 for no limit)")
    parser.add_argument("--optimized-memory", action="store_true", 
                        help="Use optimized memory processing (batch mode)")
    parser.add_argument("--traditional", action="store_true", 
                        help="Use traditional processing (load all at once)")
    args = parser.parse_args()
    
    # Determine reset behavior based on flags or user input
    should_reset = determine_reset_behavior(args.reset, args.no_reset)
    
    if should_reset:
        print("✨ Clearing Database")
        clear_database()
    
    # Determine processing mode - default to optimized unless traditional is specified
    use_optimized = not args.traditional
    
    if args.optimized_memory and args.traditional:
        print("Warning: Both --optimized-memory and --traditional flags provided.")
        print("Using optimized memory processing by default.")
        use_optimized = True
    
    if use_optimized:
        print(f"Using memory-optimized batch processing with batch size {args.batch_size}...")
        if args.memory_limit > 0:
            print(f"Memory limit set to {args.memory_limit} MB")
        process_documents_in_batches(batch_size=args.batch_size, memory_limit=args.memory_limit)
    else:
        if args.memory_limit > 0:
            print(f"Warning: Memory limit ignored in traditional processing mode")
        print("Using traditional processing (loading all documents at once)...")
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
    Loads all PDF, DOCX, and DOC files from the data directory specified by DATA_PATH.
    Uses PyMuPDFLoader for PDF files and UnstructuredWordDocumentLoader/UnstructuredFileLoader
    for DOCX/DOC files to extract content as Document objects.
    Returns a list of Document objects (pages/sections).
    """
    documents = []
    pdf_files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    docx_files = glob.glob(os.path.join(DATA_PATH, "*.docx"))
    doc_files = glob.glob(os.path.join(DATA_PATH, "*.doc"))
    
    if not pdf_files and not docx_files and not doc_files:
        print(f"No PDF, DOCX, or DOC files found in {DATA_PATH} directory.")
        return documents
    
    # Load PDF files
    for pdf_file in pdf_files:
        print(f"Loading PDF: {pdf_file}...")
        try:
            loader = PyMuPDFLoader(pdf_file)
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading PDF {pdf_file}: {e}")
    
    # Check if Unstructured loaders are available
    if UnstructuredWordDocumentLoader is None or UnstructuredFileLoader is None:
        if docx_files or doc_files:
            print("Warning: Unstructured loaders not available. Install 'unstructured' package for DOCX/DOC support.")
            print("Run: pip install unstructured")
    else:
        # Load DOCX files
        for docx_file in docx_files:
            print(f"Loading DOCX: {docx_file}...")
            try:
                loader = UnstructuredWordDocumentLoader(docx_file)
                documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading DOCX {docx_file}: {e}")
        
        # Load DOC files
        for doc_file in doc_files:
            print(f"Loading DOC: {doc_file}...")
            try:
                # For legacy .doc files, we use the more generic UnstructuredFileLoader
                loader = UnstructuredFileLoader(doc_file)
                documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading DOC {doc_file}: {e}")
    
    print(f"Loaded {len(documents)} pages/sections from {len(pdf_files)} PDF files, "
          f"{len(docx_files)} DOCX files, and {len(doc_files)} DOC files.")
    return documents


def split_documents(documents: list[Document], batch=False):
    """
    Splits a list of Document objects into smaller text chunks using RecursiveCharacterTextSplitter.
    
    Args:
        documents: List of Document objects to split
        batch: If True, process one document at a time to save memory
        
    Returns:
        A list of chunked Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    
    if batch and documents:
        # Process one document at a time to save memory
        all_chunks = []
        for i, doc in enumerate(documents):
            print(f"Splitting document {i+1}/{len(documents)}...")
            doc_chunks = text_splitter.split_documents([doc])
            all_chunks.extend(doc_chunks)
        chunks = all_chunks
    else:
        # Process all documents at once (original behavior)
        chunks = text_splitter.split_documents(documents)
        
    print(f"Split documents into {len(chunks)} chunks.")
    return chunks


def add_to_faiss(chunks: list[Document], batch_size=None):
    """
    Adds a list of chunked Document objects to the FAISS vector store.
    Loads an existing FAISS index if present, or creates a new one.
    Embeddings are generated using the embedding function from get_embedding().
    
    Args:
        chunks: List of Document objects to add to the database
        batch_size: Optional batch size for processing chunks to reduce memory usage
                   If provided, chunks will be processed in batches of this size
    """
    if not chunks:
        print("No chunks to add to database.")
        return
        
    # If batch_size is specified and valid, use batch processing
    if batch_size and isinstance(batch_size, int) and batch_size > 0:
        print(f"Using batch processing with batch size {batch_size}...")
        
        embedding_function = get_embedding()
        db = None
        
        # Load existing database if it exists
        if os.path.exists(FAISS_PATH):
            print("Loading existing FAISS index...")
            try:
                db = FAISS.load_local(str(FAISS_PATH), embedding_function, allow_dangerous_deserialization=True)
            except Exception as e:
                print(f"Error loading existing index: {e}")
                print("Will create a new FAISS index...")
                
        # Calculate IDs for all chunks
        chunks_with_ids = calculate_chunk_ids(chunks)
        total_chunks = len(chunks_with_ids)
        
        # Process in batches
        for i in range(0, total_chunks, batch_size):
            batch_end = min(i + batch_size, total_chunks)
            print(f"Processing batch {i//batch_size + 1}/{(total_chunks-1)//batch_size + 1} ({i} to {batch_end})...")
            current_batch = chunks_with_ids[i:batch_end]
            
            # Process this batch
            db = process_batch(current_batch, embedding_function, db)
        
        # Save the final database
        if db:
            db.save_local(str(FAISS_PATH))
            print(f"✅ Saved FAISS index with {total_chunks} chunks.")
        
    else:
        # Traditional processing (all at once - original behavior)
        chunks_with_ids = calculate_chunk_ids(chunks)
        embedding_function = get_embedding()

        if os.path.exists(FAISS_PATH):
            print("Loading existing FAISS index...")
            try:
                db = FAISS.load_local(str(FAISS_PATH), embedding_function, allow_dangerous_deserialization=True)
                
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
        db.save_local(str(FAISS_PATH))
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


def process_documents_in_batches(batch_size=1000, memory_limit=0):
    """
    Processes documents in batches to minimize memory usage.
    
    The function loads documents one by one, generates chunks, and adds them to the FAISS index
    in smaller batches to prevent memory overload.
    
    Args:
        batch_size (int): Number of document chunks to process in a single batch
        memory_limit (int): Memory limit in MB (0 for no limit)
    """
    try:
        import psutil
        has_psutil = True
    except ImportError:
        print("Warning: psutil not available, memory monitoring disabled")
        print("Run: pip install psutil to enable memory monitoring")
        has_psutil = False
    
    # Function to check memory usage
    def check_memory():
        if has_psutil and memory_limit > 0:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            if memory_mb > memory_limit:
                print(f"⚠️ Memory usage ({memory_mb:.1f} MB) exceeds limit ({memory_limit} MB)")
                print("Saving progress and cleaning memory...")
                return True
        return False
    
    # Get all file paths first
    pdf_files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    docx_files = glob.glob(os.path.join(DATA_PATH, "*.docx"))
    doc_files = glob.glob(os.path.join(DATA_PATH, "*.doc"))
    
    if not pdf_files and not docx_files and not doc_files:
        print(f"No PDF, DOCX, or DOC files found in {DATA_PATH} directory.")
        return
    
    # Initialize embedding function and text splitter
    embedding_function = get_embedding()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    
    # Initialize database (will be None if not exists yet)
    db = None
    if os.path.exists(FAISS_PATH):
        print("Loading existing FAISS index...")
        try:
            db = FAISS.load_local(str(FAISS_PATH), embedding_function, allow_dangerous_deserialization=True)
        except Exception as e:
            print(f"Error loading existing index: {e}")
            print("Will create a new FAISS index...")
            db = None
    
    # Track total processed chunks
    total_chunks_processed = 0
    current_batch_chunks = []
    
    # Process PDF files
    for i, pdf_file in enumerate(pdf_files):
        print(f"Processing PDF [{i+1}/{len(pdf_files)}]: {pdf_file}...")
        try:
            # Load a single document
            loader = PyMuPDFLoader(pdf_file)
            doc_chunks = loader.load()
            
            # Split into chunks and assign IDs
            chunks = text_splitter.split_documents(doc_chunks)
            chunks_with_ids = calculate_chunk_ids(chunks)
            
            # Add to current batch
            current_batch_chunks.extend(chunks_with_ids)
            
            # If batch size reached or memory limit exceeded, process batch
            if len(current_batch_chunks) >= batch_size or check_memory():
                db = process_batch(current_batch_chunks, embedding_function, db)
                total_chunks_processed += len(current_batch_chunks)
                print(f"✅ Processed {total_chunks_processed} chunks so far...")
                current_batch_chunks = []  # Clear batch
                
        except Exception as e:
            print(f"Error processing PDF {pdf_file}: {e}")
    
    # Process DOCX files if loader is available
    if UnstructuredWordDocumentLoader is not None:
        for i, docx_file in enumerate(docx_files):
            print(f"Processing DOCX [{i+1}/{len(docx_files)}]: {docx_file}...")
            try:
                # Load a single document
                loader = UnstructuredWordDocumentLoader(docx_file)
                doc_chunks = loader.load()
                
                # Split into chunks and assign IDs
                chunks = text_splitter.split_documents(doc_chunks)
                chunks_with_ids = calculate_chunk_ids(chunks)
                
                # Add to current batch
                current_batch_chunks.extend(chunks_with_ids)
                
                # If batch size reached, process batch
                if len(current_batch_chunks) >= batch_size:
                    db = process_batch(current_batch_chunks, embedding_function, db)
                    total_chunks_processed += len(current_batch_chunks)
                    print(f"✅ Processed {total_chunks_processed} chunks so far...")
                    current_batch_chunks = []  # Clear batch
                    
            except Exception as e:
                print(f"Error processing DOCX {docx_file}: {e}")
    elif docx_files:
        print("Warning: Unstructured loaders not available. Install 'unstructured' package for DOCX support.")
        print("Run: pip install unstructured")
    
    # Process DOC files if loader is available
    if UnstructuredFileLoader is not None:
        for i, doc_file in enumerate(doc_files):
            print(f"Processing DOC [{i+1}/{len(doc_files)}]: {doc_file}...")
            try:
                # Load a single document
                loader = UnstructuredFileLoader(doc_file)
                doc_chunks = loader.load()
                
                # Split into chunks and assign IDs
                chunks = text_splitter.split_documents(doc_chunks)
                chunks_with_ids = calculate_chunk_ids(chunks)
                
                # Add to current batch
                current_batch_chunks.extend(chunks_with_ids)
                
                # If batch size reached, process batch
                if len(current_batch_chunks) >= batch_size:
                    db = process_batch(current_batch_chunks, embedding_function, db)
                    total_chunks_processed += len(current_batch_chunks)
                    print(f"✅ Processed {total_chunks_processed} chunks so far...")
                    current_batch_chunks = []  # Clear batch
                    
            except Exception as e:
                print(f"Error processing DOC {doc_file}: {e}")
    elif doc_files:
        print("Warning: Unstructured loaders not available. Install 'unstructured' package for DOC support.")
        print("Run: pip install unstructured")
    
    # Process any remaining chunks in the final batch
    if current_batch_chunks:
        db = process_batch(current_batch_chunks, embedding_function, db)
        total_chunks_processed += len(current_batch_chunks)
    
    # Save the final database
    if db:
        db.save_local(str(FAISS_PATH))
        print(f"✅ Database saved with {total_chunks_processed} total chunks.")
    else:
        print("No chunks were processed. Database not updated.")


def process_batch(chunks, embedding_function, existing_db):
    """
    Process a batch of chunks and merge with existing database.
    
    Args:
        chunks: List of Document chunks to process
        embedding_function: The embedding function to use
        existing_db: Existing FAISS database or None
        
    Returns:
        Updated FAISS database
    """
    if not chunks:
        return existing_db
    
    # Display memory usage if possible
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        print(f"Current memory usage: {memory_mb:.1f} MB")
    except ImportError:
        pass
    
    print(f"Generating embeddings for {len(chunks)} chunks...")
    
    # Create new database from current batch
    new_db = FAISS.from_documents(chunks, embedding_function)
    
    # If we have an existing database, merge with it
    if existing_db is not None:
        print("Merging with existing database...")
        existing_db.merge_from(new_db)
        return existing_db
    else:
        # Otherwise, this batch becomes our database
        return new_db

if __name__ == "__main__":
    main()