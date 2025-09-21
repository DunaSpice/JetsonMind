#!/bin/bash
# Development Cycle Script - Edit, Reload, Test

echo "🚀 JetsonMind Development Cycle"
echo "================================"

# Function to reload and test
reload_and_test() {
    echo "🔄 Reloading MCP..."
    cd /home/petr/jetson/core && ./reload_mcp.sh
    
    if [ $? -eq 0 ]; then
        echo "🧪 Quick test..."
        echo -e '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "dev", "version": "1.0"}}, "id": 1}\n{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "get_system_status", "arguments": {}}, "id": 2}' | timeout 3s ./run_mcp_server.sh > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "✅ Ready for Q CLI testing!"
        else
            echo "⚠️ MCP test failed - check implementation"
        fi
    fi
}

# Watch for file changes (if inotify available)
if command -v inotifywait &> /dev/null; then
    echo "👀 Watching for changes in core/ directory..."
    echo "💡 Edit files, save, and MCP will auto-reload"
    
    while inotifywait -e modify core/*.py 2>/dev/null; do
        reload_and_test
        echo "---"
    done
else
    echo "📝 Manual mode - run './dev_cycle.sh reload' after changes"
    
    if [ "$1" = "reload" ]; then
        reload_and_test
    fi
fi
