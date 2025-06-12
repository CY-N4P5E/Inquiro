#!/usr/bin/env python3
"""
Dependency Update Helper

This script updates the project dependencies to ensure compatibility
with the latest LangChain versions and eliminates deprecation warnings.
"""

import subprocess
import sys


def main():
    print("=== RAG System Dependency Update ===")
    print("This will install or update dependencies to resolve deprecation warnings.")
    
    # Install the langchain-ollama package
    print("\n1. Installing langchain-ollama package...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", "langchain-ollama"], 
                       check=True)
        print("✅ Successfully installed langchain-ollama")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install langchain-ollama: {e}")
        return
    
    # Update other dependencies
    print("\n2. Updating core dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", 
                       "langchain", "langchain-community", "langchain-text-splitters"], 
                       check=True)
        print("✅ Successfully updated core dependencies")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update core dependencies: {e}")
    
    print("\n=== Dependency Update Complete ===")
    print("You can now run the system without deprecation warnings.")
    print("If you still see warnings, make sure any virtual environments are activated correctly.")


if __name__ == "__main__":
    main()
