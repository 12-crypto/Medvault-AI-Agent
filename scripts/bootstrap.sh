#!/bin/bash
set -e

echo "============================================"
echo "MediVault AI Agent - Bootstrap Script"
echo "============================================"

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.10"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "ERROR: Python $required_version or higher required. Found: $python_version"
    exit 1
fi
echo "✓ Python $python_version detected"

# Check Ollama
echo ""
echo "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama not found."
    echo "Please install Ollama from: https://ollama.ai/download"
    exit 1
fi
echo "✓ Ollama found: $(which ollama)"

# Check Ollama service
echo ""
echo "Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "WARNING: Ollama service not responding on localhost:11434"
    echo "Please start Ollama with: ollama serve"
else
    echo "✓ Ollama service is running"
fi

# Check required models
echo ""
echo "Checking Ollama models..."
models=$(ollama list 2>&1)

if echo "$models" | grep -q "llama3.2"; then
    echo "✓ llama3.2 model found"
else
    echo "⚠ llama3.2 model not found"
    echo "  To install: ollama pull llama3.2"
fi

if echo "$models" | grep -q "llama3.2-vision"; then
    echo "✓ llama3.2-vision model found"
else
    echo "⚠ llama3.2-vision model not found (optional for enhanced OCR)"
    echo "  To install: ollama pull llama3.2-vision"
fi

# Check Tesseract
echo ""
echo "Checking Tesseract OCR..."
if ! command -v tesseract &> /dev/null; then
    echo "⚠ Tesseract not found (required for OCR)"
    echo "  To install on macOS: brew install tesseract"
else
    echo "✓ Tesseract found: $(which tesseract)"
    echo "  Version: $(tesseract --version | head -n1)"
fi

# Create necessary directories
echo ""
echo "Creating project directories..."
mkdir -p data logs uploads temp
echo "✓ Directories created"

# Setup .env file
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    
    # Generate encryption keys
    encryption_key=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    session_secret=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Update .env with generated keys (macOS compatible)
    sed -i '' "s|ENCRYPTION_KEY=|ENCRYPTION_KEY=$encryption_key|" .env
    sed -i '' "s|SESSION_SECRET=|SESSION_SECRET=$session_secret|" .env
    
    echo "✓ .env file created with generated keys"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "============================================"
echo "Bootstrap Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Activate venv: source venv/bin/activate"
echo "2. Run application: make run"
echo "   OR: streamlit run src/app.py"
echo ""
echo "To run tests: make test"
echo "To check code: make lint"
echo ""
