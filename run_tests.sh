#!/bin/bash
# Run MuLyCue tests

echo "🧪 Running MuLyCue Tests..."
echo "================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run pytest with verbose output
pytest -v

# Show test summary
echo ""
echo "================================"
echo "✅ Tests completed!"

