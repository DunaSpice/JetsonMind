#!/bin/bash

echo "🚀 Setting up Phase 3 MCP Server"
echo "================================"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements-mcp.txt

# Make scripts executable
chmod +x mcp_server.py
chmod +x test_mcp.py

# Create MCP config directory if it doesn't exist
mkdir -p ~/.config/mcp

# Copy config to user directory
cp mcp_config.json ~/.config/mcp/phase3-config.json

echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  Start server: ./mcp_server.py"
echo "  Test server:  ./test_mcp.py"
echo "  Config file:  ~/.config/mcp/phase3-config.json"
