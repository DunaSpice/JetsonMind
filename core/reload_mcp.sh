#!/bin/bash
# MCP Hot Reload Script - Restart MCP server without Q CLI restart

echo "🔄 Reloading JetsonMind MCP Server..."

# Kill existing MCP server processes
pkill -f "mcp_server_enhanced.py" 2>/dev/null
pkill -f "run_mcp_server.sh" 2>/dev/null

# Wait for cleanup
sleep 1

# Test new MCP server
echo "🧪 Testing MCP server..."
timeout 5s ./run_mcp_server.sh < /dev/null > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ MCP server reload successful!"
    echo "💡 Q CLI will pick up changes on next tool call"
else
    echo "❌ MCP server reload failed - check syntax"
    exit 1
fi

echo "🎯 Ready for testing with Q CLI"
