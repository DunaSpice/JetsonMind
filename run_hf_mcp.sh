#!/bin/bash
# HuggingFace MCP Server wrapper with token from HF CLI

# Load HuggingFace token from CLI cache
export HUGGINGFACE_API_KEY=$(cat ~/.cache/huggingface/token)

# Run HuggingFace MCP server with stdio transport
npx huggingface-mcp-server --transport stdio
