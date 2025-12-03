#!/bin/bash

echo "============================================"
echo "Starting Ollama Service"
echo "============================================"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama not found."
    echo "Please install Ollama from: https://ollama.ai/download"
    exit 1
fi

# Check if Ollama is already running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is already running on http://localhost:11434"
    echo ""
    echo "Available models:"
    ollama list
    exit 0
fi

# Try to start Ollama service
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - try launchctl first, then fallback to direct start
    if launchctl list | grep -q "ollama"; then
        echo "✓ Ollama service is registered"
        echo "Attempting to start via launchctl..."
        launchctl start ollama 2>/dev/null || {
            echo "Launchctl start failed, starting directly..."
            ollama serve > /dev/null 2>&1 &
            sleep 3
        }
    else
        echo "Starting Ollama in background..."
        ollama serve > /dev/null 2>&1 &
        sleep 3
    fi
else
    # Linux - try systemd first, then fallback to direct start
    if systemctl is-active --quiet ollama 2>/dev/null; then
        echo "✓ Ollama service is running"
    elif systemctl start ollama 2>/dev/null; then
        echo "✓ Started Ollama service via systemd"
        sleep 2
    else
        echo "Starting Ollama in background..."
        ollama serve > /dev/null 2>&1 &
        sleep 3
    fi
fi

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
max_attempts=10
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama is now running on http://localhost:11434"
        echo ""
        echo "Available models:"
        ollama list
        exit 0
    fi
    attempt=$((attempt + 1))
    sleep 1
done

echo "ERROR: Ollama failed to start. Please check manually:"
echo "  ollama serve"
exit 1

