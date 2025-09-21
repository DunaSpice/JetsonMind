#!/usr/bin/env python3
"""
Phase 3 Web Server
HTTP interface for C frontend communication
"""

from flask import Flask, request, jsonify
import json
import asyncio
import subprocess
import sys
from pathlib import Path

app = Flask(__name__)

@app.route('/mcp', methods=['POST'])
def mcp_proxy():
    """Proxy MCP requests to the admin server"""
    try:
        data = request.get_json()
        
        # Call admin MCP server via subprocess
        cmd = [
            'bash', '-c', 
            f'cd /home/petr/jetson/phase3 && source mcp_env/bin/activate && echo \'{json.dumps(data)}\' | python3 mcp_server_admin.py'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return jsonify(json.loads(result.stdout))
        else:
            return jsonify({"error": result.stderr}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "phase3-web"})

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    app.run(host='0.0.0.0', port=port, debug=False)
