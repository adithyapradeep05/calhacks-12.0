#!/bin/bash
# Restart RAGFlow Backend Script
# This script kills any existing backend processes and starts fresh

echo "🔄 Restarting RAGFlow Backend..."
echo "================================"

# Kill any existing backend processes
echo "🛑 Stopping existing backend processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No processes on port 8000"

# Wait a moment for processes to fully stop
sleep 2

# Verify port is free
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "❌ Port 8000 is still in use. Please check manually."
    exit 1
fi

echo "✅ Port 8000 is free"

# Start Redis if not running
if ! redis-cli ping >/dev/null 2>&1; then
    echo "🔄 Starting Redis..."
    brew services start redis
    sleep 2
fi

# Start the backend
echo "🚀 Starting backend..."
/opt/anaconda3/bin/python run.py
