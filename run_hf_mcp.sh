#!/bin/bash
# HuggingFace MCP Server wrapper with token from HF CLI

# Load HuggingFace token from CLI cache and export it
export HUGGINGFACE_API_KEY=$(cat ~/.cache/huggingface/token)

# Verify token is loaded
if [ -z "$HUGGINGFACE_API_KEY" ]; then
    echo "Error: No HuggingFace token found. Run 'huggingface-cli login' first." >&2
    exit 1
fi

# Run HuggingFace MCP server with stdio transport
exec npx huggingface-mcp-server --transport stdio --api-key "$HUGGINGFACE_API_KEY"
