#!/bin/bash

# Phase 3 Complete Setup
# Installs MCP server, C frontend, and admin tools

set -e

PHASE3_DIR="/home/petr/jetson/phase3"
MCP_CONFIG="$HOME/.aws/amazonq/mcp.json"

echo "🚀 Setting up Phase 3 Complete System..."

# Setup MCP environment
echo "📦 Setting up MCP environment..."
cd "$PHASE3_DIR"
if [[ ! -d "mcp_env" ]]; then
    python3 -m venv mcp_env
fi
source mcp_env/bin/activate
pip install --upgrade pip
pip install mcp==1.14.1 flask

# Build C frontend
echo "🔨 Building C frontend..."
cd "$PHASE3_DIR/frontend"
sudo apt-get update -qq
sudo apt-get install -y libcurl4-openssl-dev libjson-c-dev gcc make
make clean && make

# Set permissions
echo "🔧 Setting permissions..."
chmod +x "$PHASE3_DIR/run_admin_server.sh"
chmod +x "$PHASE3_DIR/run_mcp_server.sh"
chmod +x "$PHASE3_DIR/frontend/build.sh"

# Test servers
echo "🧪 Testing servers..."
timeout 3s "$PHASE3_DIR/run_admin_server.sh" || echo "Admin server test completed"

# Update MCP configuration
echo "⚙️  Updating Q CLI configuration..."
python3 -c "
import json
import sys

config_file = '$MCP_CONFIG'
try:
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Backup
    with open(config_file + '.backup', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Update admin server
    config['mcpServers']['phase3-admin'] = {
        'type': 'stdio',
        'command': '$PHASE3_DIR/run_admin_server.sh',
        'args': [],
        'env': {},
        'timeout': 30,
        'disabled': False
    }
    
    # Disable basic server
    if 'phase3-inference' in config['mcpServers']:
        config['mcpServers']['phase3-inference']['disabled'] = True
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print('✅ MCP configuration updated')
except Exception as e:
    print(f'❌ MCP config error: {e}')
"

echo "✅ Phase 3 Complete System ready!"
echo ""
echo "📋 Available tools:"
echo "   • generate - Text generation"
echo "   • get_status - System status"
echo "   • start_frontend - Launch web interface"
echo "   • set_debug - Debug level control"
echo "   • get_agent_config - Agent settings"
echo "   • db_status - Database management"
echo "   • get_settings - Configuration"
echo "   • restart_service - Service control"
echo "   • get_logs - System logs"
echo ""
echo "🎯 Quick start:"
echo "   q chat 'use get_status tool'"
echo "   q chat 'use start_frontend tool'"
echo "   ./frontend/phase3_frontend"
