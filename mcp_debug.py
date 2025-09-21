#!/usr/bin/env python3
"""Minimal MCP debugging tool - MCP first approach"""

import json
import subprocess
import sys
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def test_mcp_connection():
    """Test MCP server connection"""
    try:
        result = subprocess.run([
            'python3', '/home/petr/jetson/mcp_minimal.py', '--test'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            log("✅ MCP server connection OK")
            return True
        else:
            log(f"❌ MCP connection failed: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ MCP test error: {e}")
        return False

def call_mcp_tool(tool_name, params=None):
    """Direct MCP tool call with debugging"""
    log(f"🔧 Calling MCP tool: {tool_name}")
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params or {}
        }
    }
    
    try:
        result = subprocess.run([
            'python3', '/home/petr/jetson/mcp_minimal.py', 
            '--call', json.dumps(request)
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            if response.get("success"):
                log(f"✅ Tool {tool_name} success")
                return response["result"]
            else:
                log(f"❌ Tool {tool_name} error: {response.get('error')}")
                return None
        else:
            log(f"❌ Tool {tool_name} failed: {result.stderr}")
            return None
            
    except Exception as e:
        log(f"❌ MCP call error: {e}")
        return None

def debug_session():
    """Interactive MCP debugging session"""
    log("🚀 Starting MCP debug session")
    
    # Test connection first
    if not test_mcp_connection():
        log("❌ Cannot proceed without MCP connection")
        return
        
    # Test basic tools
    tools_to_test = [
        ("debug_info", {}),
        ("get_system_status", {}),
        ("get_memory_status", {}),
        ("list_models", {})
    ]
    
    for tool, params in tools_to_test:
        result = call_mcp_tool(tool, params)
        if result:
            log(f"📊 {tool}: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    debug_session()
