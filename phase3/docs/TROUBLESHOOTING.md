# Phase 3 Troubleshooting

## Common Issues

### MCP Server Won't Start

**Error**: `'function' object is not subscriptable`
```bash
# Solution: Use isolated environment
cd /home/petr/jetson/phase3
source mcp_env/bin/activate
python3 mcp_server_minimal.py
```

**Error**: `connection closed: initialize response`
```bash
# Check MCP configuration
cat ~/.aws/amazonq/mcp.json

# Verify wrapper script is executable
chmod +x run_mcp_server.sh
```

### Q CLI Integration Issues

**Error**: `phase3-inference has failed to load`
```bash
# Check server directly
timeout 5s ./run_mcp_server.sh

# Enable debug logging
Q_LOG_LEVEL=trace q chat
```

**Error**: `validation errors for ListToolsResult`
```bash
# Update MCP version in environment
source mcp_env/bin/activate
pip install --upgrade mcp
```

### Tool Execution Problems

**Error**: `Unknown tool: [tool_name]`
- Verify tool name spelling
- Check available tools: `q chat "list tools"`

**Error**: `Tool execution failed`
- Check tool parameters match schema
- Review error message in response

## Diagnostic Commands

### Check Server Status
```bash
# Test server startup
timeout 5s ./run_mcp_server.sh

# Check environment
source mcp_env/bin/activate && python3 -c "import mcp; print(mcp.__version__)"
```

### Check Q CLI Integration
```bash
# List MCP servers
q chat --help | grep -A5 "mcp servers"

# Test with trace logging
Q_LOG_LEVEL=trace q chat "test"
```

### Check Dependencies
```bash
source mcp_env/bin/activate
pip list | grep -E "(mcp|anyio|pydantic)"
```

## Log Locations
- Q CLI logs: `$TMPDIR/qlog/qchat.log` or `/tmp/qlog/qchat.log`
- Server logs: stdout/stderr from `run_mcp_server.sh`

## Recovery Steps

### Reset Environment
```bash
rm -rf mcp_env/
python3 -m venv mcp_env
source mcp_env/bin/activate
pip install mcp==1.14.1
```

### Reset Q CLI Configuration
```bash
# Backup current config
cp ~/.aws/amazonq/mcp.json ~/.aws/amazonq/mcp.json.backup

# Remove phase3 entry and re-add
```

### Complete Reinstall
```bash
cd /home/petr/jetson/phase3
./setup.sh --clean
```
