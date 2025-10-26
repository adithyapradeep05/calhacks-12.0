#!/bin/bash
# Start RAGFlow Backend Script
# This script ensures the backend runs with the correct Python environment

echo "🚀 Starting RAGFlow Backend (Unified app.py)..."
echo "================================"

# Check if conda is available
if command -v conda &> /dev/null; then
    echo "✅ Using conda environment"
    # Use conda Python
    /opt/anaconda3/bin/python run.py
else
    echo "⚠️  Conda not found, using system Python"
    # Fallback to system Python
    python3 run.py
fi
