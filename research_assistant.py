
#!/usr/bin/env python3
"""
Interactive Research Assistant CLI
"""

import os
import sys
from query_data import query_rag


def print_banner():
    print("\n" + "="*60)
    print("    🔬 LOCAL RAG RESEARCH ASSISTANT")
    print("="*60)


def check_database():
    """Check if FAISS database exists."""
    if not os.path.exists("faiss_index"):
        print("❌ Vector database not found!")
        print("Please run: python populate_database.py")
        print("This will process your PDF files and create the database.")
        return False
    return True


def interactive_mode():
    """Run in interactive mode."""
    print_banner()
    
    if not check_database():
        return
    
    print("💡 Ask questions about your documents (type 'quit' to exit)")
    print("-" * 60)
    
    while True:
        try:
            question = input("\n🤔 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print("\n🔍 Searching documents...")
            response = query_rag(question)
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    if len(sys.argv) > 1:
        # Single question mode
        question = " ".join(sys.argv[1:])
        if check_database():
            query_rag(question)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
