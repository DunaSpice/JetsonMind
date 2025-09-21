#!/usr/bin/env python3
"""Minimal MCP server - no external dependencies"""

import json
import sys
import psutil
import platform
from datetime import datetime

class MinimalMCP:
    def __init__(self):
        self.tools = {
            "get_system_status": self.get_system_status,
            "get_memory_status": self.get_memory_status,
            "list_models": self.list_models,
            "debug_info": self.debug_info
        }
    
    def get_system_status(self, params=None):
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "platform": platform.platform(),
            "python": sys.version.split()[0]
        }
    
    def get_memory_status(self, params=None):
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / 1024**3, 1),
            "available_gb": round(mem.available / 1024**3, 1),
            "used_percent": mem.percent
        }
    
    def list_models(self, params=None):
        return {
            "models": [
                {"name": "llama-7b", "size": "7GB", "status": "available"},
                {"name": "llama-13b", "size": "13GB", "status": "available"}
            ]
        }
    
    def debug_info(self, params=None):
        return {
            "mcp_version": "minimal-1.0",
            "tools_count": len(self.tools),
            "tools": list(self.tools.keys())
        }
    
    def call_tool(self, tool_name, params=None):
        if tool_name in self.tools:
            try:
                result = self.tools[tool_name](params)
                return {"success": True, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": f"Tool {tool_name} not found"}

def main():
    mcp = MinimalMCP()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            print("MCP server test OK")
            return 0
        elif sys.argv[1] == "--call" and len(sys.argv) > 2:
            request = json.loads(sys.argv[2])
            tool_name = request["params"]["name"]
            tool_params = request["params"].get("arguments", {})
            result = mcp.call_tool(tool_name, tool_params)
            print(json.dumps(result))
            return 0
    
    # Interactive mode
    print("🚀 Minimal MCP Server Ready")
    print("Available tools:", list(mcp.tools.keys()))
    
    while True:
        try:
            tool = input("\nTool name (or 'quit'): ").strip()
            if tool == 'quit':
                break
            result = mcp.call_tool(tool)
            print(json.dumps(result, indent=2))
        except KeyboardInterrupt:
            break
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
