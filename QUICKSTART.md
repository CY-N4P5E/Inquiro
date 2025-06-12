# Inquiro Quickstart Guide

This guide will help you quickly set up and start using Inquiro, a powerful Retrieval-Augmented Generation (RAG) system for document-based question answering.

## Prerequisites

Before starting, ensure you have:

- Python 3.8 or higher installed
- Access to a terminal/command prompt
- 8GB RAM minimum (16GB recommended)
- [Ollama](https://ollama.ai) installed locally

## Step 1: Get the Code

### Option A: Clone the Repository

```powershell
git clone https://github.com/yourusername/inquiro.git
cd inquiro
```

### Option B: Download ZIP

1. Download the ZIP file from the GitHub repository
2. Extract to your desired location
3. Open a terminal and navigate to the extracted folder

## Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

If you encounter any dependency warnings later, update with:

```powershell
python update_dependencies.py
```

## Step 3: Set Up Ollama

1. Make sure [Ollama](https://ollama.ai/download) is installed and running
2. Pull the required models:
   ```powershell
   ollama pull llama3:8b
   ollama pull nomic-embed-text
   ```
3. Verify your setup:
   ```powershell
   ollama list
   ```
   
   You should see both `llama3:8b` and `nomic-embed-text` in the list.

## Step 4: Prepare Your Documents

1. Create a `data` directory if it doesn't exist:
   ```powershell
   mkdir -p data
   ```
   
2. Add your PDF documents to the `data` directory. These can be any PDF files you want to query:
   - Research papers
   - Technical documentation
   - Reports and manuals
   - Articles and publications

## Step 5: Verify Your Setup

Run the setup verification script to ensure everything is configured correctly:

```powershell
python setup_local.py
```

This will check for:
- Ollama installation and required models
- Document availability
- Python environment

## Step 6: Build Your Knowledge Base

Process your documents and create the vector database:

```powershell
python populate_database.py
```

You should see output indicating:
- Documents being loaded from the data directory
- Text being split into chunks
- Embeddings being created
- Vector database being built

If you ever want to reset and rebuild the database from scratch:

```powershell
python populate_database.py --reset
```

## Step 7: Ask Questions About Your Documents

### Interactive Mode (Recommended)

Launch the interactive research assistant:

```powershell
python research_assistant.py
```

This opens an interactive session where you can ask multiple questions in sequence.

### Single Question Mode

For one-off questions:

```powershell
python query_data.py "What does this document say about [your specific topic]?"
```

## Step 8: Run Tests (Optional)

Verify system accuracy with the test suite:

```powershell
pytest test_rag.py -v
```

## Next Steps

### Customization Options

- **Add More Documents**: Expand your knowledge base with additional PDFs
- **Tune the Prompt**: Modify the prompt template in `query_data.py` to change response style
- **Adjust Chunking**: Change the chunk size and overlap in `populate_database.py`
- **Try Different Models**: Experiment with other Ollama models like `mistral` or `codellama`

### Advanced Features

- **Build a Web UI**: Consider adding a simple web interface with Streamlit or Gradio
- **Implement Feedback**: Add a mechanism to collect and store user feedback on answers
- **Add Document Types**: Extend the system to support Word, HTML, or Markdown files
- **Batch Processing**: Process document collections in batches for improved efficiency

## Troubleshooting

If you encounter issues:

| Problem | Solution |
|---------|----------|
| **No documents found** | Make sure your PDF files are in the `data/` directory |
| **Database errors** | Try rebuilding with `python populate_database.py --reset` |
| **Ollama connection issues** | Check if Ollama is running with `ollama list` |
| **Slow responses** | Enable GPU acceleration in Ollama if available |
| **Import errors** | Run `pip install -r requirements.txt --upgrade` |

For more detailed documentation and advanced configuration options, refer to:
- [Complete Technical Documentation](DOCUMENTATION.md)
- [Technical Stack Details](TECHSTACK.md)
