#!/usr/bin/env python3
"""Quick MCP Debug Access - All Tools"""

import json
import subprocess
import sys

def call_debug_tool(tool_name, params=None):
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params or {}
        }
    }
    
    result = subprocess.run([
        'python3', '/home/petr/jetson/mcp_debug_server.py'
    ], input=json.dumps(request), capture_output=True, text=True)
    
    if result.returncode == 0:
        response = json.loads(result.stdout)
        if "result" in response:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        else:
            print(f"Error: {response.get('error')}")
            return None
    else:
        print(f"Failed: {result.stderr}")
        return None

def main():
    tools = ["debug_status", "hot_reload", "test_all_tools", "system_info", "memory_info", "process_info", "file_check", "run_command", "mcp_health", "error_trace"]
    
    if len(sys.argv) < 2:
        print("Usage: python3 debug.py <tool_name> [params_json]")
        print("Available tools:", ", ".join(tools))
        return
    
    tool_name = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    result = call_debug_tool(tool_name, params)
    if result:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
