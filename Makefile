# Makefile for epint package

VENV_PATH = /opt/envs/venv-py3.14
VENV_PYTHON = $(VENV_PATH)/bin/python
VENV_PIP = $(VENV_PATH)/bin/pip

.PHONY: help clean build install install-venv uninstall-venv run venv-activate venv-deactivate venv-shell

# Default target
help:
	@echo "Available commands:"
	@echo "  clean         - Clean build artifacts"
	@echo "  build         - Build package"
	@echo "  install       - Install package in production mode"
	@echo "  install-venv  - Install package in editable mode to $(VENV_PATH)"
	@echo "  uninstall-venv - Uninstall package from $(VENV_PATH)"
	@echo "  venv-activate  - Show command to activate venv (use: eval \$$(make venv-activate))"
	@echo "  venv-deactivate - Show command to deactivate venv"
	@echo "  venv-shell     - Start interactive shell with venv activated"
	@echo "  run <file>     - Run Python file using venv python (e.g., make run examples/usage.py)"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Clean completed."

# Build package
build: clean
	@echo "Building package..."
	python -m build
	@echo "Build completed. Distribution files are in dist/"

# Install package in production mode
install: build
	@echo "Installing package..."
	@if [ -f dist/*.whl ]; then \
		pip install dist/*.whl; \
	elif [ -f dist/*.tar.gz ]; then \
		pip install dist/*.tar.gz; \
	else \
		pip install .; \
	fi
	@echo "Installation completed."

# Install package in editable mode to venv
install-venv:
	@echo "Installing package in editable mode to $(VENV_PATH)..."
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "Error: Virtual environment not found at $(VENV_PATH)"; \
		exit 1; \
	fi
	@if $(VENV_PIP) show epint > /dev/null 2>&1; then \
		echo "Package already installed, reinstalling..."; \
		$(VENV_PIP) install --force-reinstall --no-deps -e .; \
	else \
		echo "Installing package..."; \
		$(VENV_PIP) install -e .; \
	fi
	@echo "Installation to venv completed."

# Uninstall package from venv
uninstall-venv:
	@echo "Uninstalling package from $(VENV_PATH)..."
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "Error: Virtual environment not found at $(VENV_PATH)"; \
		exit 1; \
	fi
	@if $(VENV_PIP) show epint > /dev/null 2>&1; then \
		$(VENV_PIP) uninstall -y epint; \
		echo "Package uninstalled from venv."; \
	else \
		echo "Package not installed in venv."; \
	fi

# Activate venv (use: eval $(make venv-activate))
venv-activate:
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "Error: Virtual environment not found at $(VENV_PATH)"; \
		exit 1; \
	fi; \
	echo "source $(VENV_PATH)/bin/activate"

# Deactivate venv
venv-deactivate:
	@echo "deactivate"

# Start interactive shell with venv activated
venv-shell:
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "Error: Virtual environment not found at $(VENV_PATH)"; \
		exit 1; \
	fi; \
	echo "Starting shell with venv activated..."; \
	bash -c "source $(VENV_PATH)/bin/activate && exec bash"

# Run Python file using venv python
run:
	@FILE="$(filter-out $@ venv-activate venv-deactivate venv-shell,$(MAKECMDGOALS))"; \
	if [ -z "$$FILE" ]; then \
		echo "Error: File path is required (e.g., make run examples/usage.py)"; \
		exit 1; \
	fi; \
	if [ ! -d "$(VENV_PATH)" ]; then \
		echo "Error: Virtual environment not found at $(VENV_PATH)"; \
		exit 1; \
	fi; \
	if [ ! -f "$$FILE" ]; then \
		echo "Error: File $$FILE not found"; \
		exit 1; \
	fi; \
	echo "Running $$FILE with venv python..."; \
	$(VENV_PYTHON) $$FILE

%:
	@:
