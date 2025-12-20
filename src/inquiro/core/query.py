"""
This module provides a command-line interface to query a FAISS vector database using a Retrieval-Augmented Generation (RAG) approach. 
It retrieves relevant document chunks, constructs a prompt with the context, and generates an answer using an LLM (currently Ollama).
"""

import argparse
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    
    from langchain_community.llms.ollama import Ollama

from .embedding import get_embedding
from .config import (
    FAISS_PATH, 
    OLLAMA_QUERY_MODEL, 
    FAISS_ALLOW_DANGEROUS_DESERIALIZATION,
    DEFAULT_K,
    DEFAULT_SCORE_THRESHOLD,
    DEFAULT_MAX_CONTEXT_LENGTH,
    PROMPT_TEMPLATE
)


def main():
    """
    Command-line interface entry point for the Inquiro RAG query system.
    
    Notes:
        This function assumes the system has been properly configured and validated.
        For interactive usage, consider using the dedicated UI components instead.
    """
    parser = argparse.ArgumentParser(description="Query the Inquiro RAG system")
    parser.add_argument("query_text", type=str, help="The query text")
    parser.add_argument("-k", "--top-k", type=int, default=DEFAULT_K, 
                       help=f"Number of documents to retrieve (default: {DEFAULT_K})")
    parser.add_argument("-t", "--threshold", type=float, default=DEFAULT_SCORE_THRESHOLD,
                       help=f"Minimum similarity score threshold (default: {DEFAULT_SCORE_THRESHOLD})")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Show detailed information including scores and sources")
    parser.add_argument("--stream", action="store_true",
                       help="Stream the response (if supported by model)")
    
    args = parser.parse_args()
    
    query_rag(args.query_text, k=args.top_k, threshold=args.threshold, 
             verbose=args.verbose, stream=args.stream)


def query_rag(query_text: str, k: int = DEFAULT_K, threshold: float = DEFAULT_SCORE_THRESHOLD, 
              verbose: bool = False, stream: bool = False):
    """
    Query the RAG system using the provided text.

    Args:
        query_text: The question to ask.
        k: Number of documents to retrieve.
        threshold: Minimum similarity score.
        verbose: Whether to print detailed info.
        stream: Whether to stream the response (not fully implemented).

    Returns:
        dict: A dictionary containing the answer, sources, and metadata, or None if failed.
    """
    import time
    start_time = time.time()
    
    if verbose:
        print(f"🔍 Query: {query_text}")
        print(f"📊 Retrieving top {k} documents with threshold {threshold}")
    
    # Validate query
    if not query_text.strip():
        print("❌ Error: Query cannot be empty")
        return None
    
    embedding_function = get_embedding()
    
    try:
        # Load the FAISS vector database from disk
        if verbose:
            print("📂 Loading FAISS index...")
        db = FAISS.load_local(str(FAISS_PATH), embedding_function, 
                             allow_dangerous_deserialization=FAISS_ALLOW_DANGEROUS_DESERIALIZATION)
    except Exception as e:
        print(f"❌ Error loading FAISS index: {e}")
        print("💡 Please run populate_database.py first to create the vector database.")
        return None

    # Retrieve documents with similarity scores
    try:
        results = db.similarity_search_with_score(query_text, k=k)
        
        # Filter by threshold
        filtered_results = [(doc, score) for doc, score in results if score >= threshold]
        
        if not filtered_results:
            print(f"❌ No documents found above similarity threshold {threshold}")
            print(f"💡 Try lowering the threshold or check if your query matches the document content")
            return None
        
        if verbose:
            print(f"📄 Found {len(filtered_results)} relevant documents")
            for i, (doc, score) in enumerate(filtered_results):
                source = doc.metadata.get("id", "Unknown")
                print(f"   {i+1}. Score: {score:.3f} | Source: {source}")
        
    except Exception as e:
        print(f"❌ Error during similarity search: {e}")
        return None

    # Build context and check length
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in filtered_results])
    
    if len(context_text) > DEFAULT_MAX_CONTEXT_LENGTH:
        if verbose:
            print(f"⚠️  Context too long ({len(context_text)} chars), truncating to {DEFAULT_MAX_CONTEXT_LENGTH}")
        context_text = context_text[:DEFAULT_MAX_CONTEXT_LENGTH] + "...[truncated]"

    # Generate prompt and response
    try:
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)

        if verbose:
            print("🤖 Generating response...")
        
        model = Ollama(model=OLLAMA_QUERY_MODEL)
        response_text = model.invoke(prompt)

    except Exception as e:
        print(f"❌ Error generating response: {e}")
        print("💡 Check if Ollama is running and the model is available")
        return None

    # Prepare response data
    sources = [doc.metadata.get("id", "Unknown") for doc, _score in filtered_results]
    response_time = time.time() - start_time
    
    response_data = {
        "answer": response_text,
        "sources": sources,
        "num_sources": len(sources),
        "response_time": response_time,
        "query": query_text
    }
    
    # Format and display response
    print("\n" + "="*50)
    print("🤖 Answer:")
    print(response_text)
    print("\n" + "-"*30)
    print(f"📚 Sources ({len(sources)}):")
    for i, source in enumerate(sources, 1):
        print(f"   {i}. {source}")
    
    if verbose:
        print(f"⏱️  Response time: {response_time:.2f}s")
        print("="*50)
    
    return response_data


if __name__ == "__main__":
    main()
