# Inquiro Technical Stack Specification

## Project Objective

Inquiro is a complete, production-ready RAG sys### 7. Funcements — Potential Extensions

| Feature | Implementation | Benefit |
|---------|---------------|---------|
| **PDF Highlighting** | Streamlit + PDF rendering | • Visual source attribution<br>• Direct verification of information |
| **Response Logging** | Simple file-based storage | • Record question/answer history<br>• Review previous research sessions |
| **Citation Generation** | Enhanced metadata extraction | • More detailed source referencing<br>• Improved traceability |
| **Additional Formats** | Expanded document loaders | • Support for Word, HTML, Markdown<br>• Code repository integration |
| **Custom Chunking** | Configurable chunking strategies | • Domain-specific text segmentation<br>• Improved context preservation |
| **Evaluation Tools** | Basic metrics and test cases | • System performance assessment<br>• Benchmarking RAG quality |ned to provide accurate, document-grounded responses to natural language questions. It functions as a research assistant for literature review, technical documentation, and knowledge management with an emphasis on privacy, performance, and factual accuracy.

## Development Strategy

1. **Core Functionality First**: Focus on a stable, robust core implementation before extending features
2. **CLI-based Interface**: Maintain a command-line interface for maximum flexibility and integration
3. **Progressive Enhancement**: Add features incrementally after thorough testing
4. **Privacy by Design**: Process all data locally without external API dependencies

## Technical Stack Components

### 1. LLM Backend — Ollama

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **LLM Runtime** | [Ollama](https://ollama.com/) | • Simple, one-command interface<br>• Local-first architecture for privacy<br>• Cross-platform support (Windows, macOS, Linux)<br>• Active development and strong community |
| **Primary Model** | `llama3:8b` | • Excellent reasoning capabilities<br>• Manageable resource requirements (16GB RAM)<br>• Strong performance on factual Q&A tasks<br>• Open weights enabling local deployment |
| **Alternative Models** | `mistral` or `codellama:7b` | • Lower resource requirements<br>• Faster response times<br>• Specialized capabilities (code for codellama) |

**ADR 001: Local Model Deployment**
* **Context**: Need to process potentially sensitive documents
* **Decision**: Use locally-hosted models via Ollama instead of API services
* **Consequences**: Improved privacy and reduced costs at expense of some performance
* **Status**: Accepted

**Performance Tip**: Enable GPU acceleration with `ollama run --gpu llama3:8b` for significantly improved response times.

### 2. Embedding Model — Text Representation

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Primary Embedding** | `nomic-embed-text` (via Ollama) | • High-quality embeddings (1024 dimensions)<br>• Local processing consistent with privacy goals<br>• Strong semantic understanding<br>• Efficient computation |
| **Alternative** | `bge-small-en-v1.5` (HuggingFace) | • Smaller model size<br>• Compatible with sentence-transformers<br>• Good performance on retrieval tasks |
| **Chunk Size** | 500 characters (~100-120 tokens) | • Balances context preservation with retrieval precision<br>• Avoids embedding quality degradation<br>• Optimized for technical content |
| **Chunk Overlap** | 50 characters (10%) | • Maintains context continuity<br>• Prevents information loss at chunk boundaries |

**ADR 002: Embedding Selection**
* **Context**: Need high-quality semantic search capabilities
* **Decision**: Use `nomic-embed-text` as primary embedding model
* **Alternatives Considered**: OpenAI embeddings, BGE embeddings, all-MiniLM
* **Consequences**: Strong performance with complete privacy; some additional setup required
* **Status**: Accepted

### 3. Document Processing — Loading and Chunking

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **PDF Processor** | `PyMuPDF` (via LangChain) | • High-quality text extraction<br>• Preserves document structure<br>• Handles complex PDFs including academic papers<br>• Extracts metadata (page numbers, titles) |
| **Text Chunking** | `RecursiveCharacterTextSplitter` | • Intelligent chunking respecting semantics<br>• Configurable size and overlap<br>• Preserves context within chunks<br>• Handles various languages |
| **Framework** | LangChain | • Comprehensive document processing tools<br>• Active development and support<br>• Integration with multiple vector stores<br>• Flexible component architecture |

**ADR 003: Document Processing Framework**
* **Context**: Need reliable document processing for various PDF types
* **Decision**: Use LangChain with PyMuPDF for document processing
* **Alternatives Considered**: LlamaIndex, custom processing pipeline
* **Consequences**: Simpler implementation with some tradeoffs in specialized academic parsing
* **Status**: Accepted with regular review as LlamaIndex capabilities evolve

### 4. Vector Database — FAISS

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Vector DB** | FAISS | • Industry-standard vector similarity search<br>• Highly optimized for performance<br>• Minimal resource requirements<br>• Complete offline functionality<br>• Support for millions of vectors |
| **Index Type** | Flat L2 / Inner Product | • Exact search for maximum accuracy<br>• Suitable for collections up to ~1M vectors<br>• No approximation loss |
| **Persistence** | Local file storage | • Reliable disk-based persistence<br>• No external database dependencies<br>• Portable between systems |
| **Alternative** | ChromaDB | • Better metadata filtering capabilities<br>• More complex setup<br>• Slower performance |

**ADR 004: Vector Database Selection**
* **Context**: Need efficient similarity search for document embeddings
* **Decision**: Use FAISS for vector storage and retrieval
* **Alternatives Considered**: ChromaDB, Milvus, Pinecone
* **Consequences**: Superior performance and simplicity with some limitations in complex metadata filtering
* **Status**: Accepted

### 5. RAG Pipeline — Integration Components

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Retrieval Mechanism** | `vectordb.as_retriever()` | • Configurable search parameters<br>• Integration with similarity score filtering<br>• Support for top-k retrieval logic |
| **Prompt Engineering** | Custom templating | • Explicit grounding instructions<br>• Context-focused response generation<br>• Source attribution preservation |
| **Response Generation** | Direct LLM invocation | • Fine-grained control over prompt construction<br>• Simplified debugging and tracing<br>• Custom formatting of responses |
| **Search Parameters** | k=5 with no minimum threshold | • Optimal context window utilization<br>• Balance between coverage and precision<br>• Prevents over/under retrieval |

**ADR 005: RAG Implementation Approach**
* **Context**: Need reliable, inspectable RAG implementation
* **Decision**: Use direct integration rather than high-level chain abstractions
* **Alternatives Considered**: LangChain RetrievalQA chains, LlamaIndex query engines
* **Consequences**: More control at the cost of some additional code complexity
* **Status**: Accepted

### 6. User Interface — CLI First Approach

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Primary Interface** | Command-line (CLI) | • Maximum flexibility<br>• Scriptable for automation<br>• Easier testing and debugging<br>• Lower maintenance burden |
| **Interactive Mode** | Terminal-based research assistant | • Natural conversation flow<br>• Session persistence<br>• Accessible to technical users |
| **Future UI Options** | Streamlit, Gradio, or Flask | • Web-based interface for broader accessibility<br>• Visualization of source documents<br>• Interactive refinement of queries |

**ADR 006: Interface Strategy**
* **Context**: Need reliable interface that prioritizes functionality
* **Decision**: Implement CLI first with web UI as future enhancement
* **Alternatives Considered**: Starting with web interface, desktop application
* **Consequences**: Faster development and iteration at cost of initial user experience
* **Status**: Accepted for initial phase


🧼 Don’t rush into UI until logic is stable.
🛠️ STEP 7: Optional Extras (Future Enhancements)
| Feature              | Tool                    | Notes                                 |
| -------------------- | ----------------------- | ------------------------------------- |
| PDF highlighting     | LlamaIndex + Streamlit  | Show exact chunk sources              |
| Feedback loop        | Save Q\&A sessions      | For tuning or retrying queries        |
| Citation generation  | Embed doc metadata      | Show which doc/chunk supported answer |
| Whisper integration  | Ollama or local whisper | Transcribe lecture audio if needed    |
| Markdown/HTML ingest | Python + BeautifulSoup  | Expand sources beyond PDFs            |

## Development Environment Summary

| Component | Selected Technology | Benefits |
|-----------|---------------------|---------|
| **LLM** | `llama3:8b` via Ollama | Local execution, strong reasoning |
| **Embedding** | `nomic-embed-text` via Ollama | High-quality semantic vectors |
| **Vector DB** | FAISS | Industry-standard similarity search |
| **Document Processing** | PyMuPDF + LangChain | Superior PDF handling |
| **Chunking** | RecursiveCharacterTextSplitter | Context-aware text segmentation |
| **Framework** | LangChain | Comprehensive RAG component suite |
| **Development** | Python 3.8+ | Excellent AI/ML ecosystem |
| **Deployment** | Local first, containerizable | Privacy and portability |

## System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 4 cores | 8+ cores |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 5GB + document storage | SSD preferred |
| **GPU** | Not required | CUDA-compatible (4GB+ VRAM) |
| **OS** | Windows 10+, macOS 12+, Linux | Any 64-bit OS |

For larger document collections or faster processing, scale RAM and CPU resources accordingly.
