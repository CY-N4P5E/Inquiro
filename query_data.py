
import argparse
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
# Import from the new langchain-ollama package to address deprecation warning
try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    # Fallback to community version if langchain-ollama is not installed
    from langchain_community.llms.ollama import Ollama

from get_embedding import get_embedding
from config import FAISS_PATH

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding()
    
    try:
        db = FAISS.load_local(FAISS_PATH, embedding_function, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        print("Please run populate_database.py first to create the vector database.")
        return

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Use llama3:8b 
    model = Ollama(model="llama3:8b")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text


if __name__ == "__main__":
    main()
