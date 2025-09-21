#!/usr/bin/env python3
"""Ultra-minimal MCP server - bypass library issues"""
import json
import sys

def handle_request(request):
    if request.get("method") == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "list_models",
                        "description": "List JetsonMind models",
                        "inputSchema": {"type": "object"}
                    }
                ]
            }
        }
    elif request.get("method") == "tools/call":
        return {
            "jsonrpc": "2.0", 
            "id": request.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "🤖 JetsonMind Models: gpt2-small, gpt-j-6b, llama-7b"
                    }
                ]
            }
        }
    return {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32601, "message": "Method not found"}}

# Main loop
for line in sys.stdin:
    try:
        request = json.loads(line.strip())
        response = handle_request(request)
        print(json.dumps(response), flush=True)
    except:
        pass
