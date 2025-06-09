# Technical Documentation: RAG Tutorial System

## System Architecture and Implementation Details

This document provides a comprehensive explanation of the Retrieval-Augmented Generation (RAG) system implemented in this repository. The system is designed to enhance Large Language Model (LLM) responses by grounding them in specific document collections.

## Core Components

### 1. Document Processing (`populate_database.py`)

#### Document Loading
The system uses PyPDFDirectoryLoader from LangChain to load PDF documents from the `data/` directory:

```python
def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()
```

This function loads all PDF files and converts them into LangChain `Document` objects that contain both content and metadata.

#### Document Splitting
Documents are split into smaller chunks to optimize for vector embedding and retrieval:

```python
def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)
```

The RecursiveCharacterTextSplitter divides documents into:
- **Chunk size**: 800 characters
- **Chunk overlap**: 80 characters

This approach allows the system to maintain context across chunk boundaries while keeping chunks small enough for efficient embedding and retrieval.

#### Chunk ID Generation
Each chunk is assigned a unique identifier to maintain traceability:

```python
def calculate_chunk_ids(chunks):
    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index
```

The ID format: `source_path:page_number:chunk_index` enables precise source attribution.

#### Database Management
The system implements an efficient database update mechanism that:
1. Checks existing documents in the database
2. Only adds new documents that don't already exist
3. Allows database reset with the `--reset` flag

### 2. Vector Storage and Embedding (`get_embedding_function.py`)

#### Embedding Generation
The repository supports two embedding providers:

1. **Amazon Bedrock** (default):
```python
embeddings = BedrockEmbeddings(
    credentials_profile_name="default", region_name="us-east-1"
)
```

2. **Ollama** (alternative):
```python
# embeddings = OllamaEmbeddings(model="nomic-embed-text")
```

These embedding functions convert text chunks into high-dimensional vector representations that capture semantic meaning.

#### ChromaDB Vector Storage
The system uses ChromaDB as a vector database to store and efficiently retrieve embeddings:

```python
db = Chroma(
    persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
)
```

ChromaDB provides:
- Persistent storage of embeddings
- Fast similarity search
- Document metadata storage

### 3. Query Processing (`query_data.py`)

#### Query Embedding and Retrieval
User queries follow these steps:
1. The query is transformed into a vector embedding
2. The system performs similarity search against stored document embeddings
3. The top 5 most relevant chunks are retrieved

```python
results = db.similarity_search_with_score(query_text, k=5)
```

#### Context Assembly
Retrieved document chunks are assembled into a context block:

```python
context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
```

#### Prompt Construction
The system uses a template to create a prompt that grounds the LLM in the retrieved context:

```python
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""
```

This explicit instruction helps ensure that responses are based on the document collection rather than the LLM's pre-trained knowledge.

#### LLM Response Generation
The assembled prompt is sent to the Mistral model via Ollama:

```python
model = Ollama(model="mistral")
response_text = model.invoke(prompt)
```

The final output includes both the response and the source references:

```python
formatted_response = f"Response: {response_text}\nSources: {sources}"
```

### 4. Testing and Evaluation (`test_rag.py`)

The system includes automated testing to evaluate response accuracy:

#### Test Cases
Test cases define expected responses for specific questions:

```python
def test_monopoly_rules():
    assert query_and_validate(
        question="How much total money does a player start with in Monopoly?",
        expected_response="$1500",
    )
```

#### LLM-based Evaluation
Interestingly, the system uses an LLM to evaluate the accuracy of responses:

```python
model = Ollama(model="mistral")
evaluation_results_str = model.invoke(prompt)
```

An evaluation prompt asks the model to determine if the generated response matches the expected response:

```python
EVAL_PROMPT = """
Expected Response: {expected_response}
Actual Response: {actual_response}
---
(Answer with 'true' or 'false') Does the actual response match the expected response? 
"""
```

#### Visual Feedback
Test results are displayed with color coding:
- Green for correct responses
- Red for incorrect responses

## Performance Considerations

### Embedding Efficiency
- Chunk size (800 characters) balances context retention and processing efficiency
- Chunk overlap (80 characters) helps maintain contextual continuity

### Query Optimization
- Retrieval of top 5 most similar chunks balances comprehensiveness and precision
- Similarity scores help prioritize more relevant information

### Deduplication
- The system automatically prevents duplicate documents from being added to the database
- This improves efficiency and prevents response bias from repeated information

## Extensibility

The system is designed to be extended in several ways:

### Additional Document Types
The document loading mechanism can be extended to support various file formats:
- Microsoft Word (.docx)
- HTML
- Markdown
- Plain text

### Alternative Embedding Providers
The modular design allows easy swapping of embedding providers:
- OpenAI
- Hugging Face
- Cohere
- Other local or cloud-based embedding services

### Customizable Prompt Templates
The prompt templates can be modified to:
- Change response style or format
- Include specific instructions
- Add system prompts
- Adjust context inclusion methodology

## Common Use Cases

This RAG system is particularly well-suited for:

1. **Knowledge Base Systems**
   - Internal company documentation search
   - Technical support systems
   - Product documentation QA

2. **Educational Applications**
   - Study materials and textbook interactions
   - Custom tutoring systems based on specific curricula

3. **Research Tools**
   - Literature review assistance
   - Research paper analysis
   - Domain-specific knowledge exploration

4. **Factual Grounding for Chatbots**
   - Ensuring chatbot responses are factually accurate
   - Preventing hallucination in generative AI systems

## Troubleshooting

### Common Issues and Solutions

1. **Missing Embedding Provider**
   - Ensure AWS credentials are properly set up for Bedrock
   - Or uncomment and use the Ollama embeddings option

2. **PDF Loading Failures**
   - Check that PDFs are properly formatted and not password-protected
   - Ensure the data directory contains valid PDF files

3. **Inaccurate Responses**
   - Adjust chunk size and overlap parameters
   - Increase the number of retrieved chunks (`k` parameter)
   - Refine the prompt template to better guide the LLM

4. **Performance Issues**
   - Large document collections may require increased memory
   - Consider implementing document filtering before queries
   - Optimize embedding parameters for faster processing
