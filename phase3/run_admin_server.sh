#!/bin/bash

# Phase 3 Admin MCP Server Runner
# Extended server with admin and settings tools

set -e

cd /home/petr/jetson/phase3

if [[ ! -d "mcp_env" ]]; then
    echo "Error: mcp_env not found. Run ./setup.sh first" >&2
    exit 1
fi

source mcp_env/bin/activate
exec python3 mcp_server_admin.py
