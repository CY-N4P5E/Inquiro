# Makefile for Inquiro Development
# 
# Common development tasks for Inquiro project
# Use 'make help' to see all available commands

.PHONY: help install install-dev test test-cov lint format clean build docs setup

# Default target
help:  ## Show this help message
	@echo "Inquiro Development Commands"
	@echo "=========================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup and Installation
setup: install-dev  ## Complete development setup
	@echo "Setting up development environment..."
	pre-commit install
	@echo "Development environment ready!"

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev: install  ## Install development dependencies
	pip install -r requirements-dev.txt
	pip install -e .

# Testing
test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage report
	pytest tests/ -v --cov=inquiro --cov-report=html --cov-report=term

test-watch:  ## Run tests in watch mode
	pytest-watch tests/ -- -v

# Code Quality
lint:  ## Run all linting checks
	black --check .
	isort --check-only .
	flake8 .
	pylint inquiro/
	mypy inquiro/
	bandit -r inquiro/

format:  ## Format code with black and isort
	black .
	isort .

check:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

# Documentation
docs:  ## Generate documentation
	@echo "Generating documentation..."
	@if [ -d "docs" ]; then \
		cd docs && make html; \
	else \
		echo "Documentation directory not found. Creating basic structure..."; \
		mkdir -p docs; \
		echo "Documentation generation not yet configured."; \
	fi

# Build and Distribution
build:  ## Build distribution packages
	python -m build

upload-test:  ## Upload to Test PyPI
	twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	twine upload dist/*

# Development Utilities
clean:  ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-all: clean  ## Clean everything including data
	@echo "Warning: This will remove all data and database files!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		rm -rf data/; \
		rm -rf database/; \
		rm -rf faiss_index/; \
		rm -rf C:/inquiro/; \
		echo "All data cleaned."; \
	else \
		echo ""; \
		echo "Cancelled."; \
	fi

# Inquiro Specific Commands
setup-ollama:  ## Setup Ollama models
	@echo "Installing required Ollama models..."
	ollama pull llama3:8b
	ollama pull nomic-embed-text
	@echo "Ollama models installed successfully!"

populate-db:  ## Populate the vector database
	python inquiro/core/populate_database.py

query:  ## Run a test query (interactive)
	python inquiro/core/query_data.py

cli:  ## Launch CLI interface
	python inquiro/ui/inquiro_cli.py

tui:  ## Launch TUI interface
	python inquiro/ui/inquiro_tui.py

check-setup:  ## Verify local setup
	python inquiro/ui/setup_local.py

# Development Server/Tools
dev-server:  ## Start development environment
	@echo "Starting Inquiro development environment..."
	@echo "Ollama should be running separately"
	python inquiro/ui/inquiro_tui.py

profile:  ## Profile the application
	python -m cProfile -o profile.stats inquiro/core/query_data.py "test query"
	python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

# Version Management
version:  ## Show current version
	@python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

# Security
security-check:  ## Run security checks
	bandit -r inquiro/
	pip-audit
