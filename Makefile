# Makefile for epint package

.PHONY: help clean install install-dev test lint format type-check build upload upload-test all

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install package in production mode"
	@echo "  install-dev  - Install package in development mode with dev dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black)"
	@echo "  format-check - Check code formatting"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  build        - Build package"
	@echo "  clean        - Clean build artifacts"
	@echo "  upload-test  - Upload to test PyPI"
	@echo "  upload       - Upload to PyPI"
	@echo "  all          - Run format, lint, type-check, and test"

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Install package in production mode
install:
	pip install .

# Install package in development mode
install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Run all tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=epint --cov-report=html --cov-report=term

# Run linting
lint:
	flake8 src/ tests/

# Format code
format:
	black src/ tests/
	isort src/ tests/

# Check code formatting
format-check:
	black --check src/ tests/
	isort --check-only src/ tests/

# Run type checking
type-check:
	mypy src/

# Build package
build: clean
	python -m build

# Upload to test PyPI
upload-test: build
	twine upload --repository testpypi dist/*

# Upload to PyPI
upload: build
	twine upload dist/*

# Run all quality checks
all: format lint type-check test
