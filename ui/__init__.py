"""
Windows-specific applications for Inquiro
Contains CLI and TUI applications optimized for Windows systems.
"""

from .setup_local import check_ollama, check_data_directory

__all__ = [
    'check_ollama',
    'check_data_directory'
]
