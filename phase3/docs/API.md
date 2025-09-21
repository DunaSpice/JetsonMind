# Phase 3 API Reference

## MCP Server Tools

### generate
Generate text using Phase 3 inference with automatic model selection.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "prompt": {
      "type": "string",
      "description": "Input prompt for text generation"
    }
  },
  "required": ["prompt"]
}
```

**Example Usage:**
```bash
q chat "use generate tool with prompt 'Explain quantum computing'"
```

**Response Format:**
```json
{
  "type": "text",
  "text": "Generated text for: Explain quantum computing..."
}
```

### get_status
Get Phase 3 system status and capabilities.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {}
}
```

**Example Usage:**
```bash
q chat "use get_status tool"
```

**Response Format:**
```json
{
  "status": "healthy",
  "server": "phase3-inference",
  "version": "1.0.0"
}
```

## Server Configuration

### MCP Configuration
Located in `~/.aws/amazonq/mcp.json`:
```json
{
  "phase3-inference": {
    "type": "stdio",
    "command": "/home/petr/jetson/phase3/run_mcp_server.sh",
    "timeout": 30,
    "disabled": false
  }
}
```

### Environment Variables
- `PYTHONPATH`: Set automatically by wrapper script
- `MCP_LOG_LEVEL`: Optional logging level (INFO, DEBUG, ERROR)

## Error Handling
All tools return error messages in text format when failures occur:
```json
{
  "type": "text", 
  "text": "Error: [error description]"
}
```
