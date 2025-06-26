# Inquiro Tech Stack

## Core Components

| Component         | Technology         | Purpose                                  |
|-------------------|-------------------|------------------------------------------|
| LLM Backend       | Ollama + Llama3   | Local language model for answering       |
| Embeddings        | nomic-embed-text  | High-quality vector representations      |
| Vector Database   | FAISS             | Fast similarity search                   |
| Chunking          | LangChain Splitter| Semantic text segmentation               |
| Document Loading  | PyMuPDF, Unstructured | PDF/DOCX/DOC extraction             |

## Key Features

- **Memory Optimization:**  
  Batch processing with configurable chunk size and memory limit (psutil-based monitoring).
- **Privacy:**  
  All processing is local; no data leaves your machine.

## System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU      | 4 cores | 8+ cores    |
| RAM      | 8GB     | 16GB+       |
| OS       | Win10+/macOS/Linux | 64-bit |

## Configuration

- Interactive: `python core/config.py`
- Environment variables: `DEFAULT_MEMORY_LIMIT`, etc.

## Processing Modes

| Mode              | Description                                 | Use Case                |
|-------------------|---------------------------------------------|-------------------------|
| Traditional       | All docs at once                            | Small collections       |
| Optimized Memory  | Batch by chunk count and memory monitoring  | Large collections/Low RAM|

## Extensibility

- Add new loaders for more formats (Markdown, HTML, etc.)
- Planned: PDF highlighting, response logging, citation generation

## Dependencies

See `requirements.txt` for full list.
