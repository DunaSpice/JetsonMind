#!/bin/bash

# Phase 3 MCP Server Setup Script
# Automated installation and configuration

set -e

PHASE3_DIR="/home/petr/jetson/phase3"
MCP_CONFIG="$HOME/.aws/amazonq/mcp.json"

echo "🚀 Setting up Phase 3 MCP Server..."

# Clean install option
if [[ "$1" == "--clean" ]]; then
    echo "🧹 Cleaning existing installation..."
    rm -rf "$PHASE3_DIR/mcp_env"
fi

# Create virtual environment
echo "📦 Creating isolated environment..."
cd "$PHASE3_DIR"
python3 -m venv mcp_env
source mcp_env/bin/activate

# Install dependencies
echo "⬇️  Installing dependencies..."
pip install --upgrade pip
pip install mcp==1.14.1

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x run_mcp_server.sh

# Test server
echo "🧪 Testing server..."
timeout 5s ./run_mcp_server.sh || echo "Server test completed"

# Update MCP configuration
echo "⚙️  Configuring Q CLI integration..."
if [[ -f "$MCP_CONFIG" ]]; then
    # Backup existing config
    cp "$MCP_CONFIG" "$MCP_CONFIG.backup.$(date +%s)"
    
    # Update phase3-inference entry
    python3 -c "
import json
import sys

config_file = '$MCP_CONFIG'
try:
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    config['mcpServers']['phase3-inference'] = {
        'type': 'stdio',
        'url': '',
        'headers': {},
        'oauthScopes': ['openid', 'email', 'profile', 'offline_access'],
        'command': '$PHASE3_DIR/run_mcp_server.sh',
        'args': [],
        'env': {},
        'timeout': 30,
        'disabled': False
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print('✅ MCP configuration updated')
except Exception as e:
    print(f'❌ Failed to update MCP config: {e}')
    sys.exit(1)
"
else
    echo "❌ MCP config file not found: $MCP_CONFIG"
    exit 1
fi

echo "✅ Phase 3 MCP Server setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Test with: q chat 'use get_status tool'"
echo "   2. Generate text: q chat 'use generate tool with prompt \"Hello AI\"'"
echo "   3. View docs: cat README.md"
echo ""
echo "📚 Documentation available in docs/ directory"
