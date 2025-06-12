
import argparse
import os
import shutil
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding import get_embedding
from langchain_community.vectorstores import FAISS
import glob


FAISS_PATH = "faiss_index"
DATA_PATH = "data"


def main():
    # Check if the database should be cleared (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_faiss(chunks)


def load_documents():
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
    # Use chunk sizes from techstack: 500 tokens with 50 overlap
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
    if not chunks:
        print("No chunks to add to database.")
        return

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Get embedding function
    embedding_function = get_embedding()

    # Check if FAISS index exists
    if os.path.exists(FAISS_PATH):
        print("Loading existing FAISS index...")
        try:
            db = FAISS.load_local(FAISS_PATH, embedding_function, allow_dangerous_deserialization=True)
            
            # Get existing IDs (FAISS doesn't have direct ID access, so we'll rebuild)
            print("Adding new documents to existing index...")
            
            # Create new FAISS index from all chunks
            new_db = FAISS.from_documents(chunks_with_ids, embedding_function)
            
            # Merge with existing database
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
    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(FAISS_PATH):
        shutil.rmtree(FAISS_PATH)
        print("Database cleared.")


if __name__ == "__main__":
    main()
