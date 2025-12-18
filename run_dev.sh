#!/bin/bash
# Development server launcher for MuLyCue

echo "🎵 Starting MuLyCue Development Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo "Starting FastAPI server..."
echo "Access the app at: http://localhost:8000"
python -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000

