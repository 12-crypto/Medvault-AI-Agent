.PHONY: help venv install clean test lint run check-ollama bootstrap

PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
PYTHON_VENV := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip

help:
	@echo "MediVault AI Agent - Makefile Commands"
	@echo "======================================"
	@echo "make venv          - Create Python virtual environment"
	@echo "make install       - Install dependencies"
	@echo "make bootstrap     - Complete first-time setup (venv + install + check-ollama)"
	@echo "make run           - Run Streamlit application"
	@echo "make test          - Run test suite"
	@echo "make lint          - Run linters and type checking"
	@echo "make check-ollama  - Verify Ollama installation and models"
	@echo "make clean         - Remove generated files and venv"

venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created at ./$(VENV)"

install: venv
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt -c constraints.txt
	@echo "Dependencies installed successfully"

bootstrap: venv install check-ollama
	@echo "Running bootstrap script..."
	bash scripts/bootstrap.sh
	@echo "Bootstrap complete! Run 'make run' to start the application."

check-ollama:
	@echo "Checking Ollama installation..."
	@command -v ollama >/dev/null 2>&1 || { echo "ERROR: Ollama not found. Please install from https://ollama.ai"; exit 1; }
	@ollama list | grep -q "llama3.2" || { echo "WARNING: llama3.2 model not found. Run: ollama pull llama3.2"; }
	@echo "Ollama check complete"

run:
	@echo "Starting MediVault AI Agent..."
	bash scripts/run_streamlit.sh

test:
	@echo "Running tests..."
	$(VENV_BIN)/pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	@echo "Running linters..."
	$(VENV_BIN)/black --check src/ tests/
	$(VENV_BIN)/flake8 src/ tests/ --max-line-length=120 --exclude=$(VENV)
	$(VENV_BIN)/mypy src/ --ignore-missing-imports

format:
	@echo "Formatting code..."
	$(VENV_BIN)/black src/ tests/

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf *.egg-info
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Cleanup complete"
