#!/usr/bin/env python3
"""Simple web server for C frontend"""

from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/mcp', methods=['POST'])
def mcp_proxy():
    """Simple MCP proxy - returns mock responses for testing"""
    try:
        data = request.get_json()
        tool_name = data.get('params', {}).get('name', 'unknown')
        
        # Mock responses for testing
        responses = {
            'generate': {'result': {'content': [{'type': 'text', 'text': 'Mock generated text for testing'}]}},
            'get_status': {'result': {'content': [{'type': 'text', 'text': '{"status": "healthy", "server": "phase3-admin", "version": "1.0.0"}'}]}},
            'start_frontend': {'result': {'content': [{'type': 'text', 'text': 'Frontend started on port 8080'}]}},
            'set_debug': {'result': {'content': [{'type': 'text', 'text': 'Debug level set'}]}},
            'get_agent_config': {'result': {'content': [{'type': 'text', 'text': '{"model": "gpt-4", "temperature": 0.7}'}]}},
            'db_status': {'result': {'content': [{'type': 'text', 'text': '{"connected": true, "sessions": 0}'}]}},
            'get_settings': {'result': {'content': [{'type': 'text', 'text': '{"debug_level": 1, "frontend_port": 8080}'}]}}
        }
        
        response = responses.get(tool_name, {'result': {'content': [{'type': 'text', 'text': f'Tool {tool_name} executed'}]}})
        response['jsonrpc'] = '2.0'
        response['id'] = data.get('id', 1)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": 1}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "phase3-web"})

if __name__ == '__main__':
    print("Starting Phase 3 Web Server on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False)
