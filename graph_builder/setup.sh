#!/bin/bash
# Setup script for Conference Knowledge Graph Builder

echo "====================================="
echo "Conference Knowledge Graph Builder"
echo "Setup Script"
echo "====================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed. You'll need Docker to run Memgraph."
    echo "   Install from: https://www.docker.com/products/docker-desktop"
else
    echo "✓ Docker found: $(docker --version)"
fi

echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Python dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start Memgraph (if not already running):"
echo "   docker run -p 7687:7687 -p 7444:7444 memgraph/memgraph-platform"
echo ""
echo "2. Load your presentations:"
echo "   python3 graph_builder.py '/path/to/presentations' --recursive --clear"
echo ""
echo "3. Generate agenda suggestions:"
echo "   python3 query_tools.py --action agenda"
echo ""
echo "4. Open Memgraph Lab to visualize:"
echo "   http://localhost:7444"
echo ""
echo "See README.md for detailed usage instructions."
echo ""
