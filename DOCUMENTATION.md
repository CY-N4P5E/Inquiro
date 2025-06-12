# Inquiro Technical Documentation

## System Architecture and Implementation Details

This document provides a comprehensive technical reference for Inquiro, a production-ready Retrieval-Augmented Generation (RAG) system. Inquiro enhances Large Language Model (LLM) responses by grounding them in domain-specific document collections, dramatically improving factual accuracy, relevance, and traceability of information sources.

The architecture follows modern RAG system design principles with emphasis on:

1. Efficient document processing and chunking
2. High-performance vector embeddings and similarity search
3. Context-optimized prompt engineering
4. Source attribution and response verification

## Core Components

### 1. Document Processing (`populate_database.py`)

The document processing pipeline is responsible for loading, chunking, and indexing documents to create a queryable knowledge base.

#### Document Loading
Inquiro uses PyMuPDFLoader from LangChain to load PDF documents from the `data/` directory:

```python
def load_documents():
    documents = []
    pdf_files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    
    for pdf_file in pdf_files:
        loader = PyMuPDFLoader(pdf_file)
        documents.extend(loader.load())
    
    return documents
```

This function loads all PDF files and converts them into LangChain `Document` objects that contain both content and metadata. PyMuPDF provides superior text extraction from PDFs compared to alternatives, ensuring high-quality input data.

#### Document Splitting
Documents are split into smaller chunks to optimize for vector embedding and retrieval:

```python
def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)
```

The RecursiveCharacterTextSplitter divides documents into:
- **Chunk size**: 500 characters (approximately 100-120 tokens)
- **Chunk overlap**: 50 characters (10% overlap)

This approach allows Inquiro to maintain context across chunk boundaries while keeping chunks small enough for efficient embedding and retrieval. The chunk size was carefully calibrated to balance:

1. **Contextual completeness**: Chunks must be large enough to contain complete thoughts
2. **Retrieval precision**: Smaller chunks allow for more precise retrieval of relevant information
3. **Embedding quality**: Embedding models perform optimally with text within their context window

#### Chunk ID Generation
Each chunk is assigned a unique identifier to maintain traceability throughout the system:

```python
def calculate_chunk_ids(chunks):
    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index
```

The ID format: `source_path:page_number:chunk_index` enables precise source attribution, allowing users to:
- Trace responses back to specific document pages
- Verify information accuracy against original sources
- Navigate to the original document location for additional context

#### Database Management
Inquiro implements an intelligent database update mechanism that:

1. Checks existing documents in the database
2. Only adds new documents that don't already exist
3. Allows full database reset with the `--reset` flag

This approach provides several benefits:
- **Incremental updates**: Add new documents without reprocessing the entire collection
- **Deduplication**: Prevent redundant entries when processing the same document multiple times
- **Scalability**: Efficiently handle growing document collections

### 2. Vector Storage and Embedding (`get_embedding_function.py`)

#### Embedding Generation
Inquiro uses Ollama for generating high-quality text embeddings:

```python
def get_embedding_function():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings
```

The `nomic-embed-text` model transforms text chunks into high-dimensional vector representations (1024 dimensions) that capture deep semantic meaning. This model offers an excellent balance between:

- **Quality**: Comparative performance to more expensive hosted embedding APIs
- **Efficiency**: Fast embedding generation for quick database building
- **Privacy**: All processing happens locally without sending data to external services

#### FAISS Vector Storage
Inquiro leverages Facebook AI Similarity Search (FAISS) as its vector database backend for storing and efficiently retrieving embeddings:

```python
db = FAISS.from_documents(chunks_with_ids, embedding_function)
db.save_local(FAISS_PATH)
```

FAISS provides several key advantages:

- **Performance**: Highly optimized similarity search using approximate nearest neighbors (ANN)
- **Scalability**: Efficient indexing for collections with millions of vectors
- **Persistence**: Reliable local storage with fast load times
- **Memory efficiency**: Optimized index structures for reduced RAM usage
- **Metadata preservation**: Complete document tracking with original source information

### 3. Query Processing (`query_data.py`)

The query processing component is the core of Inquiro's information retrieval system.

#### Query Embedding and Retrieval
When a user submits a question, Inquiro follows these steps:

1. The query is transformed into a vector embedding using the same embedding model as the documents
2. The system loads the FAISS index and performs similarity search against stored document embeddings
3. The top 5 most relevant chunks are retrieved with their similarity scores

```python
db = FAISS.load_local(FAISS_PATH, embedding_function, allow_dangerous_deserialization=True)
results = db.similarity_search_with_score(query_text, k=5)
```

This retrieval mechanism uses cosine similarity to identify the most semantically relevant document chunks regardless of exact keyword matches, enabling Inquiro to understand the intent behind questions and find conceptually related information.

#### Context Assembly
Retrieved document chunks are assembled into a coherent context block:

```python
context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
```

The separator formatting ensures that the LLM can distinguish between different document chunks while maintaining readability.

#### Prompt Construction
Inquiro uses a carefully designed prompt template to ground the LLM in the retrieved context:

```python
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""
```

This prompt structure incorporates several best practices:
- **Clear instruction**: Explicitly directs the model to use only the provided context
- **Context separation**: Places a clear boundary between context and question
- **Information containment**: Prevents the model from hallucinating information not in the documents
- **Repetition**: Reinforces the instruction to answer based solely on the provided context

#### LLM Response Generation
The assembled prompt is processed by the Llama 3 model via Ollama:

```python
model = Ollama(model="llama3:8b")
response_text = model.invoke(prompt)
```

Llama 3 8B was selected for its optimal balance of:
- **Performance**: Strong reasoning capabilities for synthesizing information
- **Efficiency**: Quick response times on consumer hardware
- **Size**: Reasonable memory requirements (16GB RAM recommended)

The final output includes both the response and source references for traceability:

```python
formatted_response = f"Response: {response_text}\nSources: {sources}"
```

This source attribution enables users to verify information and explore topics further in the original documents.

### 4. Testing and Evaluation (`test_rag.py`)

Inquiro includes a robust testing framework to ensure response accuracy and system reliability.

#### Test Cases
Test cases define expected responses for specific questions to verify the system's accuracy:

```python
def test_monopoly_rules():
    assert query_and_validate(
        question="How much total money does a player start with in Monopoly?",
        expected_response="$1500",
    )
```

This test-driven approach ensures:
- System reliability across updates and changes
- Consistency in response quality
- Regression detection when modifying core components

#### LLM-based Evaluation
Inquiro innovatively uses an LLM to evaluate the accuracy of responses:

```python
model = Ollama(model="mistral")
evaluation_results_str = model.invoke(prompt)
```

This approach leverages the language understanding capabilities of the LLM itself to perform sophisticated quality assessments that go beyond simple string matching. It can understand semantic equivalence and detect when responses contain the correct information even if phrased differently.

The evaluation prompt is structured to elicit a clear binary judgment:

```python
EVAL_PROMPT = """
Expected Response: {expected_response}
Actual Response: {actual_response}
---
(Answer with 'true' or 'false') Does the actual response match the expected response? 
"""
```

#### Visual Feedback
Test results are displayed with intuitive color coding:
- Green for correct responses
- Red for incorrect responses

This visual feedback mechanism makes it easy for developers to quickly identify issues during system development and tuning.

## Performance Considerations

### Embedding Efficiency
- **Chunk size optimization**: 500 characters balances context retention and processing efficiency
- **Strategic overlap**: 50 characters (10%) maintains contextual continuity across chunk boundaries
- **Embedding dimensions**: 1024-dimensional vectors provide strong semantic representation
- **Batch processing**: Documents are processed in batches to maximize throughput

### Query Optimization
- **Top-K retrieval**: Fetching the top 5 most similar chunks balances comprehensiveness and precision
- **Similarity thresholds**: System prioritizes chunks with higher semantic similarity
- **Response synthesis**: LLM consolidates information from multiple chunks to create coherent answers
- **Context window management**: Prompt design prevents context overflow for the LLM

### Resource Management
- **Memory efficiency**: FAISS indexing optimizes RAM usage even with large document collections
- **Disk storage**: Embeddings are persisted to disk with efficient serialization
- **CPU/GPU utilization**: Compatible with both CPU and GPU acceleration via Ollama
- **Incremental updates**: Only new documents are processed when updating the knowledge base

## Extensibility

Inquiro is designed with extensibility as a core principle, allowing for customization and enhancement across multiple dimensions:

### Additional Document Types
The document loading mechanism can be easily extended to support various file formats:
- **Microsoft Office**: Word (.docx), Excel (.xlsx), PowerPoint (.pptx)
- **Web content**: HTML, XML
- **Text formats**: Markdown, plain text, JSON
- **Code repositories**: Source code with specialized parsing

Implementation requires only adding the appropriate LangChain loader:
```python
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
# Then use the loader in the load_documents function
```

### Alternative Embedding Providers
Inquiro's modular architecture allows seamless swapping of embedding providers:

- **Local models**:
  - Other Ollama models via `OllamaEmbeddings`
  - Hugging Face models via `HuggingFaceEmbeddings` 
  - SentenceTransformers via `SentenceTransformerEmbeddings`

- **Cloud providers** (if internet connectivity is available):
  - OpenAI embeddings
  - Google embeddings
  - Azure embeddings

Simply modify the `get_embedding_function.py` file:
```python
def get_embedding_function():
    # Example with HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
```

### Customizable Prompt Templates
The prompt templates can be tailored to your specific use case:
- **Response format**: Change output structure (e.g., bullet points, summaries, analysis)
- **Special instructions**: Add domain-specific guidance or constraints
- **System prompts**: Include role definitions or conversation context
- **Context handling**: Modify how retrieved information is presented to the LLM
- **Multi-stage reasoning**: Implement chain-of-thought or other advanced prompting techniques

## Common Use Cases

Inquiro is designed to excel in a variety of knowledge-intensive applications:

### 1. Enterprise Knowledge Management
- **Internal Documentation**: Transform corporate wikis and knowledge bases into interactive Q&A systems
- **Technical Support**: Provide accurate answers from product documentation and support articles
- **Onboarding**: Help new employees quickly access and understand company information
- **Compliance**: Ensure responses adhere to policy guidelines and regulatory requirements

### 2. Research & Academic Applications
- **Literature Review**: Extract insights and synthesize information across multiple research papers
- **Study Assistance**: Create personalized tutoring systems based on lecture notes and textbooks
- **Thesis Development**: Organize and query research findings for academic writing
- **Grant Writing**: Reference prior work and institutional knowledge for proposal development

### 3. Content Creation & Analysis
- **Document Summarization**: Generate concise summaries of lengthy documents
- **Trend Analysis**: Identify patterns and insights across multiple documents
- **Competitive Research**: Analyze industry reports and competitor materials
- **Fact-Checking**: Verify claims against authoritative source materials

### 4. Specialized Knowledge Domains
- **Legal Research**: Navigate case law and legal documents with precise citations
- **Medical Literature**: Access clinical guidelines and research findings
- **Technical Documentation**: Query complex software or engineering documentation
- **Financial Analysis**: Extract insights from financial reports and regulatory filings

## Troubleshooting

### Common Issues and Solutions

#### 1. Installation and Configuration

| Issue | Solution |
|-------|----------|
| **Dependency Conflicts** | • Run `pip install -r requirements.txt --upgrade`<br>• If you see deprecation warnings, install `pip install langchain-ollama` |
| **Import Errors** | • Verify Python version (3.8+ required)<br>• The code includes fallback mechanisms for most dependencies |

#### 2. Ollama Integration

| Issue | Solution |
|-------|----------|
| **Connection Errors** | • Verify Ollama is installed and running (`ollama list`)<br>• Check for required models (`ollama pull llama3:8b` and `ollama pull nomic-embed-text`)<br>• Restart the Ollama service if unresponsive |
| **Slow Response Times** | • Enable GPU acceleration if available<br>• Consider using a smaller model like Mistral 7B for faster responses<br>• Set `num_ctx=2048` for reduced memory usage |

#### 3. Document Processing

| Issue | Solution |
|-------|----------|
| **PDF Loading Failures** | • Ensure PDFs aren't password-protected<br>• Check for corrupt PDF metadata<br>• Try converting problematic PDFs with a tool like Adobe Acrobat |
| **Empty or Poor Chunks** | • Adjust the `chunk_size` and `chunk_overlap` parameters<br>• Try different chunking strategies (e.g., by paragraph or heading) |

#### 4. Retrieval Quality

| Issue | Solution |
|-------|----------|
| **Inaccurate Responses** | • Increase the number of retrieved chunks (`k` parameter)<br>• Improve prompt templates with stronger guidance<br>• Experiment with different embedding models |
| **Missing Information** | • Check if the information exists in the source documents<br>• Reduce chunk size to capture more granular information<br>• Implement metadata filtering to focus on relevant document subsets |

#### 5. Performance Optimization

| Issue | Solution |
|-------|----------|
| **High Memory Usage** | • Process documents in smaller batches<br>• Use a memory-efficient index type in FAISS<br>• Implement document filtering to reduce index size |
| **Slow Database Loading** | • Consider splitting large indexes into smaller, topic-focused indexes<br>• Optimize storage with `index_store_type="flat"` for smaller collections<br>• Move the database to SSD storage for faster access |

For persistent or complex issues, refer to the [LangChain documentation](https://python.langchain.com/) or open an issue in the project repository.
