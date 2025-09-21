#!/bin/bash

# Phase 3 MCP Server Runner
# Uses isolated environment to avoid dependency conflicts
#
# This script:
# 1. Activates the isolated Python environment
# 2. Launches the Phase 3 MCP server
# 3. Handles environment setup automatically
#
# Usage: ./run_mcp_server.sh
# Called by: Amazon Q CLI via MCP configuration

set -e

# Change to Phase 3 directory
cd /home/petr/jetson/phase3

# Activate isolated environment
if [[ ! -d "mcp_env" ]]; then
    echo "Error: mcp_env not found. Run ./setup.sh first" >&2
    exit 1
fi

source mcp_env/bin/activate

# Launch MCP server
exec python3 mcp_server_minimal.py
