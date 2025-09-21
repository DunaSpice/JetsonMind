# MCP Integration Success Plan
**Date**: 2025-09-21 03:20:03 UTC-07:00  
**Goal**: Working Q CLI MCP integration with full debug capabilities

## 🎯 PHASE 1: RESEARCH & FOUNDATION (30 minutes)

### Step 1: Study Working MCP Servers (10 min)
```bash
# Find existing working MCP servers
q mcp list
pip show awslabs.aws-api-mcp-server
find ~/.local -name "*mcp*" -type f | head -10

# Examine their structure
python3 -c "import awslabs.aws_api_mcp_server; print(awslabs.aws_api_mcp_server.__file__)"
```

### Step 2: Enable Q CLI Debug Logging (5 min)
```bash
export Q_LOG_LEVEL=trace
mkdir -p /tmp/qlog
q chat --help 2>&1 | head -5
find /tmp -name "*qlog*" -o -name "*qchat*" 2>/dev/null
```

### Step 3: Analyze Transport Protocol (15 min)
```bash
# Test existing MCP server communication
strace -e trace=read,write -o /tmp/mcp_trace.log q chat &
# Examine trace for actual protocol
cat /tmp/mcp_trace.log | grep -A5 -B5 "jsonrpc"
```

## 🔧 PHASE 2: MINIMAL VIABLE SERVER (45 minutes)

### Step 4: Create Absolute Minimum Server (15 min)
```python
#!/usr/bin/env python3
# Minimal MCP server - just initialize
import json, sys
while True:
    line = sys.stdin.readline()
    if not line: break
    req = json.loads(line)
    if req.get("method") == "initialize":
        print(json.dumps({"jsonrpc":"2.0","id":req["id"],"result":{"protocolVersion":"2024-11-05","capabilities":{},"serverInfo":{"name":"minimal","version":"1.0"}}}))
```

### Step 5: Test Q CLI Loading (15 min)
```bash
# Add minimal server
q mcp add --name minimal-test --command "/home/petr/jetson/minimal_server.py"
# Check if it loads without transport errors
q chat --help 2>&1 | grep -i minimal
```

### Step 6: Add Single Tool (15 min)
```python
# Add tools/list and one simple tool
elif req.get("method") == "tools/list":
    print(json.dumps({"jsonrpc":"2.0","id":req["id"],"result":{"tools":[{"name":"ping","description":"Test tool"}]}}))
elif req.get("method") == "tools/call" and req["params"]["name"] == "ping":
    print(json.dumps({"jsonrpc":"2.0","id":req["id"],"result":{"content":[{"type":"text","text":"pong"}]}}))
```

## 🚀 PHASE 3: INCREMENTAL EXPANSION (60 minutes)

### Step 7: Add Debug Tools One by One (10 min each)
1. `system_status` - Basic system info
2. `memory_info` - Memory usage  
3. `process_info` - Process details
4. `file_check` - File operations
5. `run_command` - Command execution
6. `mcp_health` - Health checks

**Testing Protocol**: After each tool addition:
```bash
q mcp remove --name minimal-test
q mcp add --name minimal-test --command "/home/petr/jetson/minimal_server.py"
# Test tool works in Q CLI
```

## 🔍 PHASE 4: ADVANCED FEATURES (30 minutes)

### Step 8: Add Error Handling (10 min)
- Comprehensive exception catching
- Proper JSON-RPC error responses
- Logging to file for debugging

### Step 9: Add Hot Reload (10 min)
- Server restart capability
- State preservation
- Q CLI reconnection handling

### Step 10: Performance Optimization (10 min)
- Response caching
- Async operations where possible
- Memory usage optimization

## 📊 PHASE 5: VALIDATION & DOCUMENTATION (30 minutes)

### Step 11: Comprehensive Testing (15 min)
```bash
# Test all tools in Q CLI
for tool in system_status memory_info process_info file_check run_command mcp_health; do
    echo "Testing $tool in Q CLI..."
    # Use Q CLI to call each tool
done
```

### Step 12: Performance Benchmarking (10 min)
```bash
# Measure response times
time q chat "Use jetson-debug tool system_status"
# Memory usage during operation
ps aux | grep mcp_server
```

### Step 13: Update Documentation (5 min)
- Update README with success status
- Document working MCP development process
- Create usage examples

## 🎯 SUCCESS CRITERIA

### Must Have ✅
- [ ] MCP server loads in Q CLI without "Transport closed" error
- [ ] All 6 core debug tools work via Q CLI
- [ ] Server remains stable during Q CLI sessions
- [ ] Response times under 1 second per tool

### Should Have 🎯
- [ ] Hot reload functionality working
- [ ] Error handling with proper logging
- [ ] Performance optimization implemented
- [ ] Comprehensive documentation updated

### Nice to Have 💫
- [ ] Advanced debugging features
- [ ] Integration with other MCP servers
- [ ] Automated testing suite
- [ ] Community-ready documentation

## 🚨 FAILURE CHECKPOINTS

### Stop and Debug If:
- Transport closed errors persist after Phase 2
- Tools don't appear in Q CLI after Phase 3
- Server crashes during normal operation
- Response times exceed 5 seconds

### Recovery Actions:
1. Check Q CLI logs: `cat /tmp/qlog/qchat.log`
2. Test server manually: `echo '{}' | python3 server.py`
3. Compare with working MCP server behavior
4. Simplify to last working state

## ⏱️ TIME ESTIMATES

- **Phase 1**: 30 minutes (Research)
- **Phase 2**: 45 minutes (MVP)  
- **Phase 3**: 60 minutes (Tools)
- **Phase 4**: 30 minutes (Advanced)
- **Phase 5**: 30 minutes (Validation)

**Total**: 3 hours 15 minutes to complete working MCP integration

## 🔄 ITERATION STRATEGY

### If Successful:
- Continue to next phase
- Document what worked
- Commit progress to git

### If Failed:
- Stop immediately
- Analyze failure point
- Simplify to last working state
- Debug specific issue before continuing

---

**Plan Created**: 2025-09-21 03:20:03 UTC-07:00  
**Next Action**: Execute Phase 1 - Research working MCP servers  
**Success Metric**: Q CLI loads MCP server without transport errors
