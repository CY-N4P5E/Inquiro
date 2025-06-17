"""
query_data.py
-------------
This script provides a command-line interface to query a FAISS vector database using a Retrieval-Augmented Generation (RAG) approach.
It retrieves relevant document chunks based on a user query, constructs a prompt with the context, and generates an answer using an LLM (Ollama).

Main Functions:
- main(): Entry point for CLI usage. Parses the query and calls the RAG pipeline.
- query_rag(): Loads the FAISS index, retrieves relevant chunks, builds the prompt, and invokes the LLM.
"""

import argparse
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    
    from langchain_community.llms.ollama import Ollama

from core.get_embedding import get_embedding
from core.config import FAISS_PATH

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""  # The prompt template used to instruct the LLM to answer based only on retrieved context.


def main():
    """
    Entry point for the script. Parses command-line arguments to get the query text
    and calls the RAG pipeline to generate an answer.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    # Parse the query text from command-line arguments
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)


def query_rag(query_text: str):
    """
    Executes a Retrieval-Augmented Generation (RAG) pipeline:
    - Loads the FAISS vector database.
    - Retrieves the top-k most similar document chunks to the query.
    - Constructs a prompt with the retrieved context and the user query.
    - Invokes the Ollama LLM to generate an answer.
    - Prints and returns the response.
    """

    embedding_function = get_embedding()
    
    try:
        # Load the FAISS vector database from disk
        db = FAISS.load_local(FAISS_PATH, embedding_function, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        print("Please run populate_database.py first to create the vector database.")
        return

    # Retrieve the top 5 most similar document chunks to the query
    results = db.similarity_search_with_score(query_text, k=5)

    # Build the context string from the retrieved chunks
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Invoke the LLM with the constructed prompt
    model = Ollama(model="llama3:8b")
    response_text = model.invoke(prompt)

    # Collect the source IDs for traceability
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text


if __name__ == "__main__":
    main()
