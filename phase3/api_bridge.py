#!/usr/bin/env python3
"""
Phase 3 API Bridge
Provides OpenAI-compatible API that routes to Phase 3 MCP tools
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import asyncio
import subprocess
import uuid
import time

app = Flask(__name__)
CORS(app)

def call_mcp_tool(tool_name, arguments):
    """Call Phase 3 MCP tool via admin server"""
    try:
        # Create JSON-RPC request
        rpc_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Call admin server directly
        cmd = [
            'bash', '-c',
            f'cd /home/petr/jetson/phase3 && source mcp_env/bin/activate && echo \'{json.dumps(rpc_request)}\' | timeout 10s python3 -c "import sys, json; from mcp_server_admin import call_tool; import asyncio; data=json.load(sys.stdin); result=asyncio.run(call_tool(data[\'params\'][\'name\'], data[\'params\'][\'arguments\'])); print(json.dumps({{\'result\': {{\'content\': result}}}}))"'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and result.stdout.strip():
            response = json.loads(result.stdout.strip())
            return response.get('result', {}).get('content', [{}])[0].get('text', 'No response')
        else:
            return f"Error: {result.stderr or 'Unknown error'}"
            
    except Exception as e:
        return f"Error calling MCP tool: {str(e)}"

@app.route('/api/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible chat completions endpoint"""
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        # Route to appropriate Phase 3 tool based on message content
        if 'status' in user_message.lower():
            response_text = call_mcp_tool('get_status', {})
        elif 'config' in user_message.lower() or 'setting' in user_message.lower():
            response_text = call_mcp_tool('get_settings', {})
        elif 'database' in user_message.lower() or 'db' in user_message.lower():
            response_text = call_mcp_tool('db_status', {})
        else:
            # Default to generate tool
            response_text = call_mcp_tool('generate', {'prompt': user_message})
        
        # Format as OpenAI response
        response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "phase3-admin",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": len(response_text.split()),
                "total_tokens": len(user_message.split()) + len(response_text.split())
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """List available models"""
    return jsonify({
        "object": "list",
        "data": [{
            "id": "phase3-admin",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "phase3"
        }]
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "phase3-api-bridge"})

if __name__ == '__main__':
    print("Starting Phase 3 API Bridge on port 3001...")
    app.run(host='0.0.0.0', port=3001, debug=False)
