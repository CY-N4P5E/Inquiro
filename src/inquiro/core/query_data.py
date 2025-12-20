"""
query_data.py
-------------
This module provides a command-line interface to query a FAISS vector database using 
a Retrieval-Augmented Generation (RAG) approach. It retrieves relevant document chunks 
from PDF, DOCX, and DOC files based on a user query, constructs a prompt with the context, 
and generates an answer using an LLM (Ollama).

Features:
- Configurable top-k document retrieval
- Similarity score threshold filtering
- Verbose output with detailed information
- Response time tracking
- Source attribution and metadata

Dependencies:
- langchain_community: For FAISS vector store integration
- langchain.prompts: For prompt template management
- langchain_ollama/langchain_community: For Ollama LLM integration
- core.get_embedding: For embedding function
- core.config: For centralized configuration

CLI Usage:
    python query_data.py "What is machine learning?" 
    python query_data.py "question" -v -k 3 -t 0.7 --stream

Functions:
    main(): Entry point for CLI usage. Parses arguments and orchestrates the pipeline.
    query_rag(): Executes the complete RAG pipeline with configurable parameters.

Configuration:
    All configuration is imported from core.config module including:
    - FAISS_PATH: Vector database location
    - OLLAMA_QUERY_MODEL: LLM model for response generation
    - DEFAULT_K: Default number of documents to retrieve
    - DEFAULT_SCORE_THRESHOLD: Minimum similarity score
    - PROMPT_TEMPLATE: Template for context-based prompts

Author: ADPer
Version: 2.0.0
"""

import argparse
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    
    from langchain_community.llms.ollama import Ollama

from .get_embedding import get_embedding
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
    
    Provides a comprehensive CLI for querying the knowledge base with configurable
    parameters for retrieval and output formatting. Supports various options for
    customizing the query experience and response detail level.
    
    Command-Line Arguments:
        query_text (str): Required positional argument containing the user's question
        -k, --top-k (int): Number of documents to retrieve (default: from config)
        -t, --threshold (float): Minimum similarity score threshold (default: from config)  
        -v, --verbose: Enable detailed output with scores and timing information
        --stream: Enable response streaming if supported by the model
    
    Usage Examples:
        # Basic query
        python query_data.py "What is machine learning?"
        
        # Advanced query with custom parameters
        python query_data.py "technical question" -k 3 -t 0.7 -v
        
        # High-precision query
        python query_data.py "specific topic" --top-k 10 --threshold 0.8 --verbose
    
    System Requirements:
        - Configured FAISS vector database (run populate_database.py first)
        - Active Ollama service with configured models
        - Valid system configuration (run config.py setup)
    
    Error Handling:
        - Validates all input parameters before processing
        - Provides helpful error messages for common issues
        - Gracefully handles system configuration problems
        
    Output Format:
        Standard mode: Clean answer with basic source attribution
        Verbose mode: Detailed metrics, similarity scores, and timing information
    
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
    Executes a comprehensive Retrieval-Augmented Generation (RAG) pipeline.
    
    This function performs the complete RAG workflow:
    1. Loads the FAISS vector database from configured path
    2. Retrieves the top-k most similar document chunks to the query
    3. Filters results by similarity threshold to ensure relevance
    4. Constructs a context-aware prompt with retrieved documents
    5. Invokes the configured Ollama LLM to generate an answer
    6. Returns structured response with metadata and source attribution
    
    Args:
        query_text (str): The user's natural language query
        k (int, optional): Number of documents to retrieve. Defaults to DEFAULT_K.
        threshold (float, optional): Minimum similarity score for filtering. 
                                   Range 0.0-1.0. Defaults to DEFAULT_SCORE_THRESHOLD.
        verbose (bool, optional): Enable detailed output including similarity scores,
                                source information, and timing. Defaults to False.
        stream (bool, optional): Enable response streaming if supported by model.
                               Defaults to False.
    
    Returns:
        dict or None: Response dictionary containing:
            - answer (str): Generated response from the LLM
            - sources (list): List of source document IDs used for context
            - num_sources (int): Number of source documents utilized
            - response_time (float): Time taken to generate response in seconds
            - query (str): Original query text for reference
            
            Returns None if query fails due to system issues or no relevant documents.
    
    Raises:
        Exception: For system-level errors like missing FAISS index, embedding failures,
                  or LLM connectivity issues. Errors are caught and reported gracefully.
    
    Example:
        >>> result = query_rag("What is machine learning?", k=3, verbose=True)
        >>> if result:
        ...     print(f"Answer: {result['answer']}")
        ...     print(f"Sources: {result['sources']}")
    
    Notes:
        - Context length is automatically managed and truncated if needed
        - Empty queries are rejected with appropriate error messages
        - Similarity filtering helps ensure response quality and relevance
        - Source attribution enables verification and further exploration
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
