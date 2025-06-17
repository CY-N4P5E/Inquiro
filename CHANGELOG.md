# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern Python packaging with `pyproject.toml`
- Contributing guidelines (`CONTRIBUTING.md`)
- Development dependencies and tooling
- Pre-commit hooks support
- Professional project structure
- Comprehensive README with modern documentation

### Changed
- Reorganized project structure for better maintainability
- Updated documentation with professional polish
- Improved configuration management
- Enhanced error handling and user feedback

### Fixed
- Path handling across different operating systems
- Dependency version conflicts
- Documentation inconsistencies

## [0.1.0] - 2024-12-15

### Added
- Initial release of Inquiro RAG system
- PDF document processing with PyMuPDF
- Vector embedding with Nomic embed-text model
- FAISS vector database for similarity search
- Ollama integration for local LLM processing
- Command-line interface (CLI)
- Terminal user interface (TUI) with Textual
- Centralized configuration system
- Local data storage in `C:\inquiro`
- Basic test suite
- Windows PowerShell support

### Features
- **Document Processing**: Load and chunk PDF documents
- **Embedding Generation**: Create vector embeddings for semantic search
- **Query Processing**: Natural language query interface
- **Source Attribution**: Track and cite document sources
- **Local Processing**: Complete privacy with no external API calls
- **Multi-Interface**: CLI, TUI, and programmatic access

### Supported Models
- Language Model: Llama 3 (8B parameter)
- Embedding Model: Nomic Embed Text
- Vector Database: FAISS (CPU optimized)

### Requirements
- Python 3.8+
- Ollama runtime
- 8GB+ RAM recommended
- Windows/macOS/Linux support

---

## Version History Summary

| Version | Date | Key Features |
|---------|------|--------------|
| 0.1.0 | 2024-12-15 | Initial release with core RAG functionality |
| 0.2.0 | TBD | Professional packaging and enhanced documentation |

## Migration Guides

### From 0.1.x to 0.2.x
- No breaking changes expected
- Enhanced configuration options available
- New development tools and workflows
- Improved documentation and examples

## Acknowledgments

Special thanks to:
- LangChain team for the excellent RAG framework
- Ollama for making local LLMs accessible
- Nomic for high-quality embedding models
- FAISS team for efficient vector search
- All contributors and testers
