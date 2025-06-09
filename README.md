# RAG Tutorial: Building a Retrieval-Augmented Generation System

## Overview

This repository demonstrates a complete implementation of a Retrieval-Augmented Generation (RAG) system. RAG combines the power of large language models (LLMs) with information retrieval to generate more accurate, relevant, and factual responses based on specific document collections. Unlike traditional LLMs which rely solely on their pre-trained knowledge, RAG systems can access, retrieve, and utilize specific information from custom document collections.

## Project Purpose

This project serves as:
- A working example of a RAG system using LangChain and ChromaDB
- A demonstration of embedding generation and vector similarity search
- A reference implementation for document chunking and processing
- A tutorial on how to ground LLM responses in specific document sources
- A template for building RAG-based applications

## How It Works

### System Architecture

The RAG implementation in this repository consists of four main components:

1. **Document Processing Pipeline**
   - Loads PDFs from the `data/` directory
   - Splits documents into manageable text chunks
   - Maintains document metadata for source attribution

2. **Vector Database**
   - Converts text chunks into vector embeddings
   - Stores embeddings in ChromaDB for efficient similarity search
   - Implements deduplication and document versioning

3. **Query Engine**
   - Takes natural language questions as input
   - Finds semantically similar document chunks
   - Constructs context-rich prompts for the LLM

4. **Response Generation**
   - Processes prompts with relevant retrieved context
   - Generates answers using an LLM (Mistral via Ollama)
   - Returns answers with source attribution

### Data Flow

```
┌───────────┐    ┌──────────────┐    ┌──────────────┐
│  PDF Docs │───►│Text Chunking │───►│  Embedding   │
└───────────┘    └──────────────┘    └──────────────┘
                                            │
                                            ▼
                 ┌──────────────┐    ┌──────────────┐
┌───────────┐    │    Query     │    │   ChromaDB   │
│ User Query│───►│  Processing  │◄───│Vector Storage│
└───────────┘    └──────────────┘    └──────────────┘
                        │
                        ▼
                 ┌──────────────┐    ┌──────────────┐
                 │Context-based │    │    LLM       │
                 │   Prompt     │───►│  Response    │
                 └──────────────┘    └──────────────┘
```

## File Structure

- **`populate_database.py`**: Handles document loading, splitting, and vector database management
- **`query_data.py`**: Processes questions, retrieves relevant context, and generates responses
- **`get_embedding_function.py`**: Provides embedding functions using Amazon Bedrock or Ollama
- **`test_rag.py`**: Contains tests to evaluate the system's response accuracy
- **`data/`**: Directory containing PDF documents used as knowledge sources
- **`chroma/`**: Directory where the vector database is stored (created at runtime)

## Setup and Usage

### Prerequisites

- Python 3.8+
- Required packages (install with `pip install -r requirements.txt`)
- AWS credentials configured for Amazon Bedrock (or Ollama installed locally)
- PDF documents in the `data/` directory

### Installation

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/rag-tutorial-v2.git
   cd rag-tutorial-v2
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your embedding provider
   - For Amazon Bedrock: ensure AWS credentials are set up
   - For Ollama: uncomment the Ollama embeddings line in `get_embedding_function.py`

### Building the Knowledge Base

To process documents and build the vector database:

```bash
python populate_database.py
```

To reset the database and rebuild it from scratch:

```bash
python populate_database.py --reset
```

### Querying the System

To ask questions about documents in your knowledge base:

```bash
python query_data.py "What is the starting money in Monopoly?"
```

### Running Tests

To evaluate the system's accuracy:

```bash
pytest test_rag.py -v
```

## Customization

- **Embedding Models**: Edit `get_embedding_function.py` to change the embedding provider
- **Document Types**: Extend `populate_database.py` to support additional document formats
- **Chunking Strategy**: Modify the chunking parameters in `split_documents()` function
- **Prompt Template**: Customize the prompt template in `query_data.py` for different response styles

## Technical Details

### Document Chunking

Documents are split into chunks of 800 characters with 80-character overlaps. This balances context retention with embedding efficiency.

### Chunk Identification

Each chunk gets a unique identifier in the format:
```
source_path:page_number:chunk_index
```
This allows for source attribution and tracing responses back to specific document sections.

### Similarity Search

When querying, the system retrieves the top 5 most semantically similar chunks using vector similarity search.

### Context Assembly

Retrieved chunks are concatenated to form a comprehensive context, which is included in the prompt to the LLM.

## Future Improvements

- Support for more document types (Word, HTML, Markdown, etc.)
- Implementation of hybrid search (combining vector and keyword search)
- Integration of document metadata filtering
- User interface for easier interaction

## License

[License information here]

## Acknowledgments

- LangChain for providing the RAG framework
- ChromaDB for vector storage capabilities
