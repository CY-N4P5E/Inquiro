# Contributing to Inquiro

We love your input! We want to make contributing to Inquiro as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 🚀 Quick Start for Contributors

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/inquiro.git
   cd inquiro
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e .[dev]
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

### Testing Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=inquiro

# Run specific test
pytest tests/test_rag.py -v

# Lint your code
black .
flake8 .
mypy inquiro/
```

## 📋 Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/amazing-feature
# or
git checkout -b bugfix/fix-issue-123
```

### 2. Make Your Changes
- Write clean, readable code
- Add tests for new functionality
- Update documentation as needed
- Follow our coding standards

### 3. Test Your Changes
```bash
# Ensure all tests pass
pytest

# Check code formatting
black --check .
flake8 .
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add amazing feature"
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `style:` formatting changes
- `refactor:` code refactoring
- `test:` adding tests
- `chore:` maintenance tasks

### 5. Push and Create Pull Request
```bash
git push origin feature/amazing-feature
```

Then create a pull request on GitHub.

## 🐛 Bug Reports

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/yourusername/inquiro/issues).

**Great Bug Reports** tend to have:
- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## 💡 Feature Requests

We welcome feature requests! Please:
1. Check if the feature already exists or is planned
2. Open an issue describing:
   - **Problem**: What problem does this solve?
   - **Solution**: Describe your proposed solution
   - **Alternatives**: Any alternative solutions considered
   - **Context**: Any additional context or screenshots

## 🎨 Coding Standards

### Python Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length: 88 characters
- Use type hints where appropriate

### Code Organization
- Keep functions small and focused
- Use descriptive variable and function names
- Add docstrings to public functions and classes
- Group related functionality into modules

### Example Function
```python
def process_document(file_path: str, chunk_size: int = 500) -> List[Document]:
    """Process a document into chunks for embedding.
    
    Args:
        file_path: Path to the document file
        chunk_size: Maximum size of each text chunk
        
    Returns:
        List of document chunks
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If chunk_size is invalid
    """
    # Implementation here
    pass
```

### Documentation
- Use clear, concise language
- Include code examples where helpful
- Update README.md for user-facing changes
- Add inline comments for complex logic

## 🧪 Testing Guidelines

### Test Structure
```python
def test_function_name():
    # Arrange
    input_data = "test input"
    expected = "expected output"
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected
```

### Test Coverage
- Aim for high test coverage (>80%)
- Test both happy paths and edge cases
- Include integration tests for workflows
- Mock external dependencies (Ollama, file system)

## 📖 Documentation

### Code Documentation
- Use Google-style docstrings
- Document all public APIs
- Include usage examples
- Keep documentation up-to-date

### User Documentation
- Update README.md for user-facing changes
- Add examples for new features
- Update troubleshooting section as needed

## 🔄 Pull Request Process

1. **Ensure CI passes**: All tests and checks must pass
2. **Update documentation**: Include relevant documentation updates
3. **Add tests**: New features should include tests
4. **Small, focused PRs**: Easier to review and merge
5. **Clear description**: Explain what and why, not just how

### Pull Request Template
Your PR should include:
- **Summary**: What does this PR do?
- **Changes**: List of changes made
- **Testing**: How was this tested?
- **Screenshots**: If UI changes
- **Breaking Changes**: Any breaking changes?

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🤝 Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
Examples of behavior that contributes to creating a positive environment include:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

## 🆘 Getting Help

- **Documentation**: Check the [README](README.md) and [Wiki](https://github.com/yourusername/inquiro/wiki)
- **Issues**: Search existing [issues](https://github.com/yourusername/inquiro/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/yourusername/inquiro/discussions)

## 🏗️ Project Structure

```
inquiro/
├── inquiro/              # Main package
│   ├── core/            # Core RAG functionality
│   ├── ui/              # User interfaces
│   └── __init__.py
├── tests/               # Test suite
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── requirements.txt     # Dependencies
├── pyproject.toml       # Project configuration
└── README.md           # Project overview
```

Thank you for contributing to Inquiro! 🚀
