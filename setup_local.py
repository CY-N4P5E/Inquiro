
#!/usr/bin/env python3
"""
Local setup script for the RAG research assistant.
This script helps verify that all required components are available.
"""

import subprocess
import sys
import os
from config import DATA_PATH, FAISS_PATH


def check_ollama():
    """Check if Ollama is installed and running."""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed and running")
            
            # Check for required models
            models = result.stdout
            required_models = ['llama3:8b', 'nomic-embed-text']
            missing_models = []
            
            for model in required_models:
                if model not in models:
                    missing_models.append(model)
            
            if missing_models:
                print(f"❌ Missing required models: {missing_models}")
                print("Run the following commands to install them:")
                for model in missing_models:
                    print(f"  ollama pull {model}")
                return False
            else:
                print("✅ All required Ollama models are available")
                return True
        else:
            print("❌ Ollama is not running")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        print("Please install Ollama from https://ollama.ai")
        return False


def check_data_directory():
    """Check if data directory exists and has PDF files."""
    if not os.path.exists(DATA_PATH):
        print("❌ Data directory not found")
        print("Creating data directory...")
        os.makedirs(DATA_PATH)
        print("✅ Data directory created")
        print(f"Please add PDF files to the {DATA_PATH} directory")
        return False
    
    pdf_files = [f for f in os.listdir(DATA_PATH) if f.endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDF files found in data directory")
        print(f"Please add PDF files to the {DATA_PATH} directory")
        return False
    
    print(f"✅ Found {len(pdf_files)} PDF files in data directory")
    return True


def main():
    print("🔍 Checking local RAG setup...")
    print("=" * 50)
    
    ollama_ok = check_ollama()
    data_ok = check_data_directory()
    
    print("=" * 50)
    
    if ollama_ok and data_ok:
        print("🎉 Setup complete! You can now:")
        print("1. Run: python populate_database.py")
        print("2. Query: python query_data.py 'your question here'")
    else:
        print("❌ Setup incomplete. Please address the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
