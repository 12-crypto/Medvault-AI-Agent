#!/bin/bash

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found. Run 'make venv install' first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found. Using .env.example defaults."
    echo "Run 'make bootstrap' to generate .env with secure keys."
fi

# Check and start Ollama if needed
echo "Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Ollama is not running. Starting Ollama..."
    bash scripts/start_ollama.sh
    echo ""
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run Streamlit
echo "Starting MediVault AI Agent on http://localhost:8501"
streamlit run src/app.py \
    --server.port=8501 \
    --server.address=localhost \
    --server.headless=true \
    --browser.gatherUsageStats=false
