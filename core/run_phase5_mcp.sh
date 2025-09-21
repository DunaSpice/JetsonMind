#!/bin/bash
# Phase 5 MCP Server Runner - Intelligent AI Architecture

cd "$(dirname "$0")"

# Set Python path
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Run Phase 5 MCP server
exec python3 mcp_server_phase5.py
