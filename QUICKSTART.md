# Quickstart Guide - RAG Tutorial

This quickstart guide will help you set up and run the Retrieval Augmented Generation (RAG) system.

## Prerequisites

Before starting, ensure you have:

- Python 3.8 or higher installed
- Git installed
- Access to a terminal/command prompt
- Either:
  - AWS account with Bedrock access (preferred)
  - Ollama installed locally with the Mistral model

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/rag-tutorial-v2.git
cd rag-tutorial-v2
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Configure Embedding Provider

### Option A: Use AWS Bedrock (Default)
1. Ensure AWS CLI is installed and configured
2. Verify your credentials in `~/.aws/credentials`
3. Make sure your AWS region has Bedrock available

### Option B: Use Ollama (Local)
1. [Install Ollama](https://ollama.ai/download)
2. Pull the required models:
   ```bash
   ollama pull mistral
   ollama pull nomic-embed-text
   ```
3. Edit `get_embedding_function.py` to use Ollama embeddings:
   ```python
   def get_embedding_function():
       # embeddings = BedrockEmbeddings(
       #     credentials_profile_name="default", region_name="us-east-1"
       # )
       embeddings = OllamaEmbeddings(model="nomic-embed-text")
       return embeddings
   ```

## Step 4: Prepare Document Data

1. Create a `data` directory if it doesn't exist:
   ```bash
   mkdir -p data
   ```
2. Add PDF documents to the `data` directory

## Step 5: Build the Vector Database

```bash
python populate_database.py
```

You should see output indicating documents being processed and added to the database.

## Step 6: Query the System

Try asking a question from your documents:

```bash
python query_data.py "What is the rule for passing Go in Monopoly?"
```

## Step 7: Run Tests (Optional)

```bash
pytest test_rag.py -v
```

## Next Steps

- Add more PDF documents to expand your knowledge base
- Customize prompt templates in `query_data.py`
- Adjust chunking parameters in `populate_database.py`
- Experiment with different embedding models

## Troubleshooting

If you encounter issues:

1. **Database Problems**: Try rebuilding the database with `python populate_database.py --reset`
2. **Embedding Errors**: Verify your AWS credentials or Ollama installation
3. **Missing Dependencies**: Run `pip install -r requirements.txt` again

For more detailed documentation, refer to `DOCUMENTATION.md`.
