#!/bin/bash
# MCP Debug Server Runner for Q CLI
cd /home/petr/jetson
exec python3 mcp_debug_server.py "$@"
