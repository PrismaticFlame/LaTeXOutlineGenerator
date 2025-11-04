#!/bin/bash
set -e

# Start Ollama in the background
echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
sleep 5

# Check if model exists, if not pull it
MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
echo "Checking for model: $MODEL"
if ! ollama list | grep -q "$MODEL"; then
    echo "Pulling model $MODEL (this may take a few minutes)..."
    ollama pull "$MODEL"
else
    echo "Model $MODEL already available"
fi

# Run the Python script with all arguments passed to the container
echo "Running PDF outliner..."
python outline.py "$@"

# Cleanup
kill $OLLAMA_PID 2>/dev/null || true