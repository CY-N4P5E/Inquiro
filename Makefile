.PHONY : install install-dev clean help
.DEFAULT_GOAL := help

# =========================
# Installation targets
# =========================

install:
	@echo "Installing production dependencies..."
	pip install -e .
	@echo "Installation complete."

install-dev:
	@echo "Installing development dependencies..."
	pip install -e .[dev]
	@echo "Development installation complete."

# =========================
# Clean targets
# =========================

clean:
	@echo "Cleaning up build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Cleanup complete."

# =========================
# Miscellaneous targets
# =========================

help:
	@echo "Please specify a target. Available targets are:"
	@echo "  install       - Install production dependencies"
	@echo "  install-dev   - Install development dependencies"
	@echo "  clean         - Clean up build artifacts"