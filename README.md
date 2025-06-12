# Inquiro

<div align="center">
    <img src="https://via.placeholder.com/200x200.png?text=Inquiro" alt="Inquiro Logo" width="200"/>
    <p><em>Knowledge at your fingertips through document-grounded AI</em></p>
</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

**Inquiro** is a powerful Retrieval-Augmented Generation (RAG) system that enhances Large Language Model (LLM) responses by grounding them in your own document collections. This approach dramatically improves factual accuracy, relevance, and traceability of information sources compared to traditional LLMs that rely solely on pre-trained knowledge.

By combining sophisticated document processing, high-performance vector search, and advanced prompt engineering, Inquiro delivers precise, contextually relevant answers to your questions with clear source attribution.

## Key Features

- **✨ Document-Grounded Responses**: Bases answers on your specific document collection, not generic LLM knowledge
- **🔍 Advanced Semantic Search**: Utilizes high-quality vector embeddings for accurate information retrieval
- **📄 PDF Support**: Process and analyze PDF documents with clean text extraction
- **🔗 Source Attribution**: Provides clear references to source documents for all information
- **🚀 Local-First Architecture**: Runs entirely on your local machine with no data sent to external servers
- **⚡ Ollama Integration**: Works with Llama 3 and other models via Ollama's efficient local runtime

## System Architecture

```
┌───────────┐    ┌──────────────┐    ┌──────────────┐
│  PDF Docs │───►│Text Chunking │───►│  Embedding   │
└───────────┘    └──────────────┘    └──────────────┘
                                        │
                                        ▼
┌───────────┐    ┌──────────────┐    ┌──────────────┐
│ User Query│───►│    Query     │◄───│   FAISS DB   │
└───────────┘    │  Processing  │    │Vector Storage│
                 └──────────────┘    └──────────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │  LLM-based   │
                 │   Response   │
                 └──────────────┘
```

Inquiro provides a robust pipeline for document processing, vector storage, and query handling:

1. **Document Processing**: PDF documents are loaded, split into optimal chunks, and assigned tracking IDs
2. **Vector Storage**: Document chunks are transformed into embeddings and stored in a FAISS database
3. **Query Engine**: Natural language questions are processed to find semantically similar document chunks
4. **Response Generation**: A context-aware prompt combines retrieved information for accurate answers

## Quick Start

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai) installed locally
- PDF documents you want to query

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/inquiro.git
cd inquiro

# Install dependencies
pip install -r requirements.txt

# Install required Ollama models
ollama pull llama3:8b
ollama pull nomic-embed-text

# Verify setup
python setup_local.py
```

### Usage

1. **Add your documents**
   ```
   mkdir -p data
   # Copy your PDF files to the data/ directory
   ```

2. **Build the knowledge base**
   ```
   python populate_database.py
   ```

3. **Query using the research assistant**
   ```
   python research_assistant.py
   ```

For detailed instructions, see [QUICKSTART.md](QUICKSTART.md).

## Use Cases

Inquiro is ideal for:

- **Research Assistance**: Analyze and query research papers or technical documents
- **Knowledge Management**: Create searchable repositories of organizational knowledge
- **Education**: Build customized learning tools based on specific curricula
- **Documentation Search**: Make technical documentation easily queryable

## Documentation

- [Quick Start Guide](QUICKSTART.md) - Get up and running quickly
- [Technical Documentation](DOCUMENTATION.md) - Detailed technical reference
- [Technical Stack](TECHSTACK.md) - Component choices and architecture decisions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

### Using the Research Assistant

The system provides an interactive research assistant interface:

```powershell
python research_assistant.py
```

This launches an interactive CLI where you can ask multiple questions in sequence.

For single queries, use:

```powershell
python query_data.py "Your question here"
```

### Running Tests

To validate system functionality:

```powershell
pytest test_rag.py -v
```

## Handling Deprecation Warnings

If you see deprecation warnings related to LangChain Ollama components, update your dependencies:

```powershell
pip install langchain-ollama
```

This will install the updated packages that resolve warnings about `OllamaEmbeddings` and `Ollama` classes that will be removed in future LangChain versions.
```

### Usage

#### Interactive Mode (Recommended)
```powershell
python research_assistant.py
```

#### Single Question Mode
```powershell
python research_assistant.py "What is the main topic of the document?"
```

#### Direct Query (Advanced)
```powershell
python query_data.py "Your question here"
```

### Running Tests

To evaluate the system's accuracy:

```powershell
pytest test_rag.py -v
```

## Customization

- **Embedding Models**: Edit `get_embedding_function.py` to change the embedding provider
- **Document Types**: Extend `populate_database.py` to support additional document formats

## Troubleshooting

- **Database Issues**: Rebuild the database with `python populate_database.py --reset`
- **Embedding Errors**: Verify your Ollama installation and model availability
- **Missing Dependencies**: Run `pip install -r requirements.txt` again

For more detailed technical information, see `DOCUMENTATION.md`.
