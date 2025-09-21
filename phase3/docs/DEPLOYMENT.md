# Phase 3 Deployment Guide

## Prerequisites
- Python 3.10+
- Amazon Q CLI installed
- Virtual environment support

## Installation Steps

### 1. Environment Setup
```bash
cd /home/petr/jetson/phase3
python3 -m venv mcp_env
source mcp_env/bin/activate
pip install --upgrade pip
pip install mcp==1.14.1
```

### 2. Server Configuration
```bash
# Make wrapper executable
chmod +x run_mcp_server.sh

# Test server
timeout 5s ./run_mcp_server.sh
```

### 3. Q CLI Integration
Add to `~/.aws/amazonq/mcp.json`:
```json
{
  "mcpServers": {
    "phase3-inference": {
      "type": "stdio",
      "command": "/home/petr/jetson/phase3/run_mcp_server.sh",
      "args": [],
      "env": {},
      "timeout": 30,
      "disabled": false
    }
  }
}
```

### 4. Verification
```bash
# Test Q CLI integration
q chat "list available tools"

# Test Phase 3 tools
q chat "use get_status tool"
```

## Automated Setup
Use the provided setup script:
```bash
./setup.sh
```

## Directory Structure
```
phase3/
├── mcp_env/                    # Isolated Python environment
│   ├── bin/activate           # Environment activation
│   └── lib/python3.10/        # Dependencies
├── mcp_server_minimal.py       # Main server code
├── run_mcp_server.sh          # Wrapper script
└── inference/                 # Core inference logic
```

## Dependencies
- `mcp==1.14.1` - Model Context Protocol
- `anyio>=4.10.0` - Async I/O
- `pydantic>=2.11.0` - Data validation
- `httpx>=0.28.1` - HTTP client

## Performance
- **Startup Time**: ~1 second
- **Memory Usage**: ~50MB base
- **Tool Response**: <100ms typical
