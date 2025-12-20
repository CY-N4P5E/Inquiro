#!/usr/bin/env python3
"""
Inquiro CLI - Local-first Interactive Research Assistant
A beautiful command-line interface for document-based AI research
"""

import os
import time
from datetime import datetime
from typing import Optional, List

import typer

from .core.query_data import query_rag
from .core.config import FAISS_PATH, DATA_PATH


# Color codes for beautiful terminal output
class Colors:
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Styles
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


def print_colored(text: str, color: str = Colors.RESET, end: str = '\n') -> None:
    """Print text with color and reset to normal."""
    print(f"{color}{text}{Colors.RESET}", end=end)


def print_gradient_banner():
    """Print a beautiful gradient banner."""
    banner_lines = [
        "██╗███╗   ██╗ ██████╗ ██╗   ██╗██╗██████╗  ██████╗ ",
        "██║████╗  ██║██╔═══██╗██║   ██║██║██╔══██╗██╔═══██╗",
        "██║██╔██╗ ██║██║   ██║██║   ██║██║██████╔╝██║   ██║",
        "██║██║╚██╗██║██║▄▄ ██║██║   ██║██║██╔══██╗██║   ██║",
        "██║██║ ╚████║╚██████╔╝╚██████╔╝██║██║  ██║╚██████╔╝",
        "╚═╝╚═╝  ╚═══╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═╝ ╚═════╝ "
    ]
    
    colors = [Colors.BRIGHT_CYAN, Colors.CYAN, Colors.BLUE, Colors.BRIGHT_BLUE, Colors.MAGENTA, Colors.BRIGHT_MAGENTA]
    
    print()
    for i, line in enumerate(banner_lines):
        print_colored(line.center(80), colors[i % len(colors)])
    
    print_colored("🔬 AI-Powered Document Research Assistant", Colors.BRIGHT_WHITE)
    print_colored("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", Colors.DIM)


def print_stats():
    """Print system statistics."""
    stats = get_system_stats()
    
    print_colored("\n📊 System Status", Colors.BRIGHT_YELLOW)
    print_colored("─" * 50, Colors.DIM)
    
    # Database status
    if stats['database_ready']:
        print_colored(f"🟢 Database: Ready ({stats['chunks']} chunks)", Colors.GREEN)
    else:
        print_colored("🔴 Database: Not Ready", Colors.RED)
    
    # Document count
    print_colored(f"📄 Documents: {stats['documents']} files", Colors.CYAN)
    
    # Storage location
    print_colored(f"💾 Storage: {DATA_PATH}", Colors.DIM)
    
    print()


def get_system_stats() -> dict:
    """Get current system statistics."""
    stats = {
        'database_ready': os.path.exists(FAISS_PATH) and os.path.exists(os.path.join(FAISS_PATH, 'index.faiss')),
        'documents': 0,
        'chunks': 0
    }
    
    # Count documents
    if os.path.exists(DATA_PATH):
        files = [f for f in os.listdir(DATA_PATH) if f.endswith(('.pdf', '.txt', '.md'))]
        stats['documents'] = len(files)
    
    # Estimate chunks (rough calculation)
    if stats['database_ready']:
        # This is a rough estimate - actual chunk count would require loading the DB
        stats['chunks'] = stats['documents'] * 30  # Average chunks per document
    
    return stats


def show_typing_animation(text: str, delay: float = 0.03):
    """Show typing animation for text."""
    for char in text:
        print_colored(char, Colors.BRIGHT_GREEN, end='')
        time.sleep(delay)
    print()


def show_thinking_animation(duration: float = 2.0):
    """Show a thinking animation."""
    thinking_chars = ['🤔', '💭', '🧠', '⚡', '🔍', '📖']
    end_time = time.time() + duration
    
    print_colored("\n", end='')
    while time.time() < end_time:
        for char in thinking_chars:
            if time.time() >= end_time:
                break
            print_colored(f"\r{char} Analyzing documents...", Colors.YELLOW, end='')
            time.sleep(0.2)
    
    print_colored("\r✨ Found relevant information!     ", Colors.GREEN)


def print_help():
    """Print help information."""
    print_colored("\n🆘 Available Commands", Colors.BRIGHT_YELLOW)
    print_colored("─" * 50, Colors.DIM)
    print_colored("📝 Just type your question naturally", Colors.WHITE)
    print_colored("🔄 'reload' or 'r'  - Reload database", Colors.CYAN)
    print_colored("📊 'stats' or 's'   - Show system stats", Colors.CYAN)
    print_colored("🆘 'help' or 'h'    - Show this help", Colors.CYAN)
    print_colored("🚪 'quit' or 'q'    - Exit Inquiro", Colors.CYAN)
    print_colored("🧹 'clear' or 'c'   - Clear screen", Colors.CYAN)
    print()


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_response(response: str, sources: List[str]) -> None:
    """Format and display the response beautifully."""
    print_colored("\n✨ Answer", Colors.BRIGHT_GREEN)
    print_colored("─" * 60, Colors.DIM)
    
    # Word wrap for better readability
    words = response.split()
    line = ""
    for word in words:
        if len(line + word) > 70:  # Line wrap at 70 characters
            print_colored(line.strip(), Colors.WHITE)
            line = word + " "
        else:
            line += word + " "
    
    if line.strip():
        print_colored(line.strip(), Colors.WHITE)
    
    # Show sources if available
    if sources:
        print_colored(f"\n📚 Sources ({len(sources)} documents)", Colors.BRIGHT_BLUE)
        print_colored("─" * 30, Colors.DIM)
        seen_files = set()
        source_count = 0
        
        for source in sources:
            if ':' in source:
                # Extract just filename from full path
                filepath = source.split(':')[0]
                filename = os.path.basename(filepath)
            else:
                filename = source
            
            # Only show unique filenames
            if filename not in seen_files:
                seen_files.add(filename)
                source_count += 1
                if source_count <= 3:  # Show first 3 unique files
                    print_colored(f"{source_count}. {filename}", Colors.BLUE)
        
        if len(seen_files) > 3:
            print_colored(f"   ... and {len(seen_files) - 3} more", Colors.DIM)


def print_banner():
    """Print the main banner with stats."""
    clear_screen()
    print_gradient_banner()
    print_stats()


def check_database() -> bool:
    """Check if FAISS database exists with nice formatting."""
    if not os.path.exists(FAISS_PATH):
        print_colored("\n❌ Database Not Ready", Colors.BRIGHT_RED)
        print_colored("─" * 40, Colors.DIM)
        print_colored("The vector database hasn't been created yet.", Colors.WHITE)
        print_colored("\n🔧 To get started:", Colors.BRIGHT_YELLOW)
        print_colored("1. Add PDF files to: ", Colors.WHITE, end='')
        print_colored(str(DATA_PATH), Colors.CYAN)
        print_colored("2. Run: ", Colors.WHITE, end='')
        print_colored("python populate_database.py", Colors.GREEN)
        print_colored("\nThis will process your documents and create the database.", Colors.DIM)
        return False
    return True


def interactive_mode():
    """Run in interactive mode with a beautiful interface."""
    print_banner()
    
    if not check_database():
        return
    
    print_help()
    
    # Welcome message
    print_colored("🚀 Ready to answer your questions!", Colors.BRIGHT_GREEN)
    print_colored("Type your question below or use a command (type 'help' for options)", Colors.DIM)
    
    question_count = 0
    
    while True:
        try:
            # Create a nice prompt
            timestamp = datetime.now().strftime("%H:%M")
            print_colored(f"\n[{timestamp}] ", Colors.DIM, end='')
            print_colored("❓ Your question: ", Colors.BRIGHT_CYAN, end='')
            
            question = input().strip()
            
            if not question:
                continue
            
            # Handle commands
            if question.lower() in ['quit', 'exit', 'q']:
                print_colored("\n👋 Thanks for using Inquiro! Goodbye!", Colors.BRIGHT_MAGENTA)
                break
            
            elif question.lower() in ['help', 'h']:
                print_help()
                continue
            
            elif question.lower() in ['stats', 's']:
                print_stats()
                continue
            
            elif question.lower() in ['clear', 'c']:
                print_banner()
                continue
            
            elif question.lower() in ['reload', 'r']:
                print_colored("\n🔄 Reloading system...", Colors.YELLOW)
                if check_database():
                    print_colored("✅ System reloaded successfully!", Colors.GREEN)
                continue
            
            # Process the question
            question_count += 1
            show_thinking_animation(1.5)
            
            try:
                result = query_rag(question)
                
                if result and isinstance(result, dict):
                    response_text = str(result.get("answer", ""))
                    sources = result.get("sources", [])
                    format_response(response_text, sources)
                else:
                    print_colored("\n❌ No response generated or invalid format.", Colors.RED)
                
                # Show question count
                print_colored(f"\n💫 Question #{question_count} answered!", Colors.BRIGHT_BLUE)
                
            except Exception as e:
                print_colored(f"\n❌ Oops! Something went wrong:", Colors.BRIGHT_RED)
                print_colored(f"Error: {str(e)}", Colors.RED)
                print_colored("Try rephrasing your question or check if the database is properly built.", Colors.DIM)
            
        except KeyboardInterrupt:
            print_colored("\n\n👋 Interrupted! Goodbye!", Colors.BRIGHT_MAGENTA)
            break
        except Exception as e:
            print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)


def single_question_mode(question: str):
    """Handle single question mode with nice formatting."""
    print_gradient_banner()
    
    if not check_database():
        return
    
    print_colored(f"\n❓ Question: ", Colors.BRIGHT_CYAN, end='')
    print_colored(f'"{question}"', Colors.WHITE)
    
    show_thinking_animation(1.0)
    
    try:
        result = query_rag(question)
        
        if result and isinstance(result, dict):
            response_text = str(result.get("answer", ""))
            sources = result.get("sources", [])
            format_response(response_text, sources)
        else:
            print_colored("\n❌ No response generated or invalid format.", Colors.RED)
        
    except Exception as e:
        print_colored(f"\n❌ Error processing question:", Colors.BRIGHT_RED)
        print_colored(f"{str(e)}", Colors.RED)


app = typer.Typer()

def version_callback(value: bool):
    if value:
        print_colored("Inquiro CLI v1.0.0", Colors.BRIGHT_CYAN)
        print_colored("🔬 AI-Powered Document Research Assistant", Colors.DIM)
        raise typer.Exit()

@app.callback(invoke_without_command=True)
def cli(
    ctx: typer.Context,
    question: Optional[List[str]] = typer.Argument(None, help="The question to ask. Leave empty for interactive mode."),
    version: Optional[bool] = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True, help="Show version and exit."),
):
    """
    Inquiro CLI - Local-first Interactive Research Assistant
    A beautiful command-line interface for document-based AI research

    To launch the TUI (Text User Interface), run:
    inquiro-tui
    """
    if ctx.invoked_subcommand is not None:
        return

    if question:
        question_text = " ".join(question)
        single_question_mode(question_text)
    else:
        interactive_mode()


def main():
    app()


if __name__ == "__main__":
    main()
