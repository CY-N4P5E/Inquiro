'''
Configuration file for Inquiro RAG system.

This file contains all the default and recommended options necessary for the functioning of the Retrieval-Augmented Generation (RAG) system. It provides essential information such as model configuration, database paths, and data storage locations.

Sections:
- Base directory setup: Determines the root directory for all Inquiro data based on the operating system.
- Data storage paths: Specifies where data and vector database (FAISS) indices are stored.
- Model configuration: Sets the default models for querying and embeddings used by the RAG pipeline.
- Text processing: Configures chunking parameters for document splitting.
- Query settings: Configures retrieval and response generation parameters.

Variables:
- INQUIRO_BASE_DIR: Root directory for Inquiro data (OS-dependent).
- DATA_PATH: Directory for storing data files.
- FAISS_PATH: Directory for storing FAISS vector database indices.
- OLLAMA_QUERY_MODEL: Default model used for answering queries.
- OLLAMA_EMBEDDING_MODEL: Default model used for generating embeddings.
- CHUNK_SIZE: Size of text chunks for document splitting.
- CHUNK_OVERLAP: Overlap between consecutive chunks.
- DEFAULT_K: Default number of documents to retrieve.
- DEFAULT_SCORE_THRESHOLD: Minimum similarity score for retrieval.
- DEFAULT_MAX_CONTEXT_LENGTH: Maximum context length for LLM input.
- PROMPT_TEMPLATE: Template for RAG prompts.

Environment Variables (all optional):
- INQUIRO_BASE_DIR: Override base directory
- OLLAMA_QUERY_MODEL: Override query model
- OLLAMA_EMBEDDING_MODEL: Override embedding model
- CHUNK_SIZE: Override chunk size
- CHUNK_OVERLAP: Override chunk overlap
- DEFAULT_K: Override retrieval count
- DEFAULT_SCORE_THRESHOLD: Override similarity threshold
- DEFAULT_MAX_CONTEXT_LENGTH: Override max context length
- DEFAULT_MEMORY_LIMIT: Override memory limit for processing
- FAISS_ALLOW_DANGEROUS_DESERIALIZATION: Override FAISS safety setting
- PROMPT_TEMPLATE: Override prompt template

Author: ADPer
Version: 2.0.0
'''

import os
import subprocess
from pathlib import Path

# Base directory for all Inquiro data storage based on the operating system
# Can be overridden with INQUIRO_BASE_DIR environment variable
_default_base_dir = Path.home() / "inquiro"
INQUIRO_BASE_DIR = Path(os.getenv("INQUIRO_BASE_DIR", _default_base_dir))

# Data storage directories
DATA_PATH = str(INQUIRO_BASE_DIR / "data")
FAISS_PATH = str(INQUIRO_BASE_DIR / "database" / "faiss_index")

# Default ollama model configuration (can be overridden with environment variables)
OLLAMA_QUERY_MODEL = os.getenv("OLLAMA_QUERY_MODEL", "CognitiveComputations/dolphin-mistral:7b")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# Text chunking configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))

# FAISS configuration
FAISS_ALLOW_DANGEROUS_DESERIALIZATION = os.getenv("FAISS_ALLOW_DANGEROUS_DESERIALIZATION", "true").lower() == "true"

# Memory optimization configuration
DEFAULT_MEMORY_LIMIT = int(os.getenv("DEFAULT_MEMORY_LIMIT", "8000"))  # In MB, 0 means no limit

# Query/RAG configuration
DEFAULT_K = int(os.getenv("DEFAULT_K", "7"))  # Number of documents to retrieve
DEFAULT_SCORE_THRESHOLD = float(os.getenv("DEFAULT_SCORE_THRESHOLD", "0.4"))  # Minimum similarity score threshold
DEFAULT_MAX_CONTEXT_LENGTH = int(os.getenv("DEFAULT_MAX_CONTEXT_LENGTH", "6000"))  # Maximum context length in characters

# Prompt template for RAG queries
PROMPT_TEMPLATE = os.getenv("PROMPT_TEMPLATE", """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
""")

# Checking if the directories exist, if not, create them
def ensure_directories():
    """
    Ensures that the necessary directories for data and FAISS index exist.
    Creates them if they do not already exist.
    
    Raises:
        PermissionError: If directories cannot be created due to permissions
        OSError: If directories cannot be created due to other OS-level issues
    """
    directories = [
        ("Data", DATA_PATH),
        ("FAISS Index", FAISS_PATH)
    ]
    
    for name, path in directories:
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            print(f"   ✓ {name} directory: {path}")
        except PermissionError:
            raise PermissionError(f"Permission denied: Cannot create {name} directory at {path}")
        except OSError as e:
            raise OSError(f"Failed to create {name} directory at {path}: {e}")

# Checking the OLLAMA models are set correctly
def check_ollama_models():
    """
    Checks if the user's system has ollama setup properly and the models installed.
    If Ollama is not installed, it raises an error.
    If the models are missing, it asks the user to install or choose different models.
    """
    import subprocess
    
    try:
        # Check if ollama is installed and accessible
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        available_models = result.stdout
        
        # Check if required models are available
        query_model_available = OLLAMA_QUERY_MODEL in available_models
        embedding_model_available = OLLAMA_EMBEDDING_MODEL in available_models
        
        if not query_model_available or not embedding_model_available:
            print(f"Missing models detected:")
            if not query_model_available:
                print(f"  - Query model '{OLLAMA_QUERY_MODEL}' not found")
            if not embedding_model_available:
                print(f"  - Embedding model '{OLLAMA_EMBEDDING_MODEL}' not found")
            
            print(f"\nAvailable models:\n{available_models}")
            
            choice = input("Do you want to (1) install missing models or (2) choose different models? [1/2]: ").strip()
            
            if choice == "1":
                install_missing_models(query_model_available, embedding_model_available)
            elif choice == "2":
                choose_alternative_models(available_models)
            else:
                raise ValueError("Invalid choice. Please run the configuration again.")
                
    except subprocess.CalledProcessError:
        raise EnvironmentError("Ollama is not installed or not accessible. Please install Ollama to use this system.")
    except FileNotFoundError:
        raise EnvironmentError("Ollama command not found. Please ensure Ollama is installed and in your PATH.")


def install_missing_models(query_available, embedding_available):
    """Install missing ollama models."""
    if not query_available:
        print(f"Installing query model: {OLLAMA_QUERY_MODEL}")
        subprocess.run(["ollama", "pull", OLLAMA_QUERY_MODEL], check=True)
    
    if not embedding_available:
        print(f"Installing embedding model: {OLLAMA_EMBEDDING_MODEL}")
        subprocess.run(["ollama", "pull", OLLAMA_EMBEDDING_MODEL], check=True)
    
    print("✅ All required models are now installed!")


def choose_alternative_models(available_models):
    """Allow user to choose alternative models from available ones."""
    global OLLAMA_QUERY_MODEL, OLLAMA_EMBEDDING_MODEL
    
    print("Choose alternative models from available ones:")
    
    query_model = input(f"Enter the model name for querying (current: {OLLAMA_QUERY_MODEL}): ").strip()
    if query_model:
        OLLAMA_QUERY_MODEL = query_model
    
    embedding_model = input(f"Enter the model name for embeddings (current: {OLLAMA_EMBEDDING_MODEL}): ").strip()
    if embedding_model:
        OLLAMA_EMBEDDING_MODEL = embedding_model
    
    print(f"✅ Updated models - Query: {OLLAMA_QUERY_MODEL}, Embedding: {OLLAMA_EMBEDDING_MODEL}")


def validate_config():
    """
    Validates the current configuration settings.
    Checks for reasonable values and warns about potential issues.
    """
    issues = []
    
    # Check chunk size configuration
    if CHUNK_SIZE < 100:
        issues.append(f"CHUNK_SIZE ({CHUNK_SIZE}) is very small, consider using at least 100")
    elif CHUNK_SIZE > 2000:
        issues.append(f"CHUNK_SIZE ({CHUNK_SIZE}) is very large, consider using less than 2000")
    
    if CHUNK_OVERLAP >= CHUNK_SIZE:
        issues.append(f"CHUNK_OVERLAP ({CHUNK_OVERLAP}) should be smaller than CHUNK_SIZE ({CHUNK_SIZE})")
    
    # Check query configuration
    if DEFAULT_K < 1:
        issues.append(f"DEFAULT_K ({DEFAULT_K}) must be at least 1")
    elif DEFAULT_K > 20:
        issues.append(f"DEFAULT_K ({DEFAULT_K}) is very large, consider using less than 20")
    
    if not (0.0 <= DEFAULT_SCORE_THRESHOLD <= 1.0):
        issues.append(f"DEFAULT_SCORE_THRESHOLD ({DEFAULT_SCORE_THRESHOLD}) should be between 0.0 and 1.0")
    
    if DEFAULT_MAX_CONTEXT_LENGTH < 1000:
        issues.append(f"DEFAULT_MAX_CONTEXT_LENGTH ({DEFAULT_MAX_CONTEXT_LENGTH}) is very small, consider at least 1000")
    
    # Check memory limit
    try:
        import psutil
        total_memory_mb = psutil.virtual_memory().total / (1024 * 1024)
        if DEFAULT_MEMORY_LIMIT > total_memory_mb * 0.9:
            issues.append(f"DEFAULT_MEMORY_LIMIT ({DEFAULT_MEMORY_LIMIT} MB) is too close to total memory ({total_memory_mb:.0f} MB)")
    except ImportError:
        pass  # Skip memory validation if psutil not available
    
    # Check if base directory is writable
    try:
        test_file = INQUIRO_BASE_DIR / "test_write.tmp"
        test_file.touch()
        test_file.unlink()
    except (PermissionError, OSError) as e:
        issues.append(f"Cannot write to base directory {INQUIRO_BASE_DIR}: {e}")
    
    # Warn about issues
    if issues:
        print("⚠️  Configuration warnings:")
        for issue in issues:
            print(f"   - {issue}")
        print()
    
    return len(issues) == 0


def get_config_summary():
    """
    Returns a summary of the current configuration.
    """
    # Try to get system memory info
    try:
        import psutil
        total_memory_mb = psutil.virtual_memory().total / (1024 * 1024)
        memory_info = f"{total_memory_mb:.0f} MB"
        recommended_limit = max(int(total_memory_mb * 0.7), 1000)
        memory_recommendation = f"(Recommended limit: {recommended_limit} MB)"
    except ImportError:
        memory_info = "Unknown (install psutil for memory monitoring)"
        memory_recommendation = ""
        
    return f"""
📋 Inquiro Configuration Summary:
   Base Directory: {INQUIRO_BASE_DIR}
   Data Path: {DATA_PATH}
   FAISS Path: {FAISS_PATH}
   
   Models:
   Query Model: {OLLAMA_QUERY_MODEL}
   Embedding Model: {OLLAMA_EMBEDDING_MODEL}
   
   System Resources:
   Total Memory: {memory_info}
   Memory Limit: {'None' if DEFAULT_MEMORY_LIMIT <= 0 else f"{DEFAULT_MEMORY_LIMIT} MB"} {memory_recommendation}
   
   Text Processing:
   Chunk Size: {CHUNK_SIZE}
   Chunk Overlap: {CHUNK_OVERLAP}
   
   Query Settings:
   Default K (retrieved docs): {DEFAULT_K}
   Score Threshold: {DEFAULT_SCORE_THRESHOLD}
   Max Context Length: {DEFAULT_MAX_CONTEXT_LENGTH}
"""


def validate_system():
    """
    Validates that the system is properly configured and ready to use.
    Checks FAISS index, embedding function, and Ollama model availability.
    
    Returns:
        bool: True if system is ready, False if there are issues
    """
    issues = []
    
    # Check if FAISS index exists
    if not os.path.exists(FAISS_PATH):
        issues.append(f"FAISS index not found at {FAISS_PATH}")
    
    # Check if embedding function works
    try:
        from core.get_embedding import get_embedding
        embedding_function = get_embedding()
        test_embedding = embedding_function.embed_query("test")
        if not test_embedding:
            issues.append("Embedding function not working properly")
                
    except Exception as e:
        issues.append(f"Embedding function error: {e}")
    
    # Check if Ollama model is accessible
    try:
        try:
            from langchain_ollama import OllamaLLM as Ollama
        except ImportError:
            from langchain_community.llms.ollama import Ollama
        
        model = Ollama(model=OLLAMA_QUERY_MODEL)
        # Don't actually invoke to avoid unnecessary API calls
    except Exception as e:
        issues.append(f"Ollama model '{OLLAMA_QUERY_MODEL}' not accessible: {e}")
    
    if issues:
        print("❌ System validation failed:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    
    print("✅ System validation passed")
    return True


def configure_memory_limit():
    """
    Configure memory limit for database operations.
    Prompts the user to set a memory limit based on system resources.
    
    Returns:
        int: The configured memory limit in MB (0 means no limit)
    """
    global DEFAULT_MEMORY_LIMIT
    
    try:
        import psutil
        total_memory_mb = psutil.virtual_memory().total / (1024 * 1024)
        recommended_limit = max(int(total_memory_mb * 0.7), 1000)
        
        memory_choice = input(f"Set memory limit for database operations? [Y/n]: ").strip().lower()
        if memory_choice in ['', 'y', 'yes']:
            try:
                memory_limit = input(f"Enter memory limit in MB (recommended: {recommended_limit}, current: {DEFAULT_MEMORY_LIMIT}, 0 for no limit): ").strip()
                if memory_limit:
                    DEFAULT_MEMORY_LIMIT = int(memory_limit)
                    if DEFAULT_MEMORY_LIMIT > 0:
                        print(f"✅ Memory limit set to {DEFAULT_MEMORY_LIMIT} MB")
                    else:
                        print("✅ No memory limit set (use with caution)")
            except ValueError:
                print(f"Invalid input. Using default memory limit: {DEFAULT_MEMORY_LIMIT}")
        else:
            print(f"✅ Using current memory limit: {'None' if DEFAULT_MEMORY_LIMIT <= 0 else f'{DEFAULT_MEMORY_LIMIT} MB'}")
    except ImportError:
        print("Warning: psutil not available, memory monitoring disabled")
        print("Run: pip install psutil to enable memory monitoring")
    
    return DEFAULT_MEMORY_LIMIT


# main function

def main():
    """
    Main configuration setup function.
    Ensures directories exist, validates configuration, and checks model availability.
    """
    print("🔧 Setting up Inquiro configuration...")
    
    try:
        # Create necessary directories
        ensure_directories()
        print("✅ Directories created/verified")
        
        # Configure system resources (memory only)
        print("\n📊 System resource configuration:")
        configure_memory_limit()
        
        # Validate basic configuration
        validate_config()
        
        # Check ollama models
        print("\n🤖 Model configuration:")
        check_ollama_models()
        print("✅ Ollama models verified")
        
        # Validate entire system
        validate_system()
        
        # Print configuration summary
        print(get_config_summary())
        
        print("🎉 Configuration setup complete!")
        
    except Exception as e:
        print(f"❌ Configuration setup failed: {e}")
        raise

if __name__ == "__main__":
    main()