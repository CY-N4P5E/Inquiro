#!/usr/bin/env python3
import subprocess
import sys
import os
from core.config import DATA_PATH


def check_ollama():
    """
    Checks if the Ollama tool is installed and running, and verifies that required models are available.
    Prints status messages for the user and instructions if models are missing or Ollama is not installed.
    Returns:
        bool: True if Ollama is running and all required models are available, False otherwise.
    """
    try:
        # Try to list Ollama models to check if Ollama is running
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed and running")
            models = result.stdout
            required_models = ['llama3:8b', 'nomic-embed-text']
            missing_models = []
            # Check for each required model
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
        # Ollama command not found
        print("❌ Ollama is not installed")
        print("Please install Ollama from https://ollama.ai")
        return False


def check_data_directory():
    """
    Checks if the data directory exists and contains PDF files.
    If the directory does not exist, it is created and the user is prompted to add PDF files.
    Returns:
        bool: True if the data directory exists and contains PDF files, False otherwise.
    """
    if not os.path.exists(DATA_PATH):
        print("❌ Data directory not found")
        print("Creating data directory...")
        os.makedirs(DATA_PATH)
        print("✅ Data directory created")
        print(f"Please add PDF files to the {DATA_PATH} directory")
        return False
    # List PDF files in the data directory
    pdf_files = [f for f in os.listdir(DATA_PATH) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"Please add PDF files to the {DATA_PATH} directory")
        return False
    print(f"✅ Found {len(pdf_files)} PDF files in data directory")
    return True


def main():
    """
    Main entry point for local setup verification.
    Checks Ollama installation and model availability, and verifies the data directory setup.
    Provides user instructions based on the results.
    """
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
