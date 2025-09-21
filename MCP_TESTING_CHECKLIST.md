# MCP Testing Checklist - Proper Development Process

## ❌ WRONG WAY (What We Did)
- [x] Test with manual JSON-RPC: `echo '{}' | python3 server.py`
- [x] Test interactive mode: `python3 server.py --interactive`  
- [x] Test direct tool calls: `python3 debug.py tool_name`
- [x] Assume stdio transport works with Q CLI
- [x] Add features before basic connection works

## ✅ RIGHT WAY (What We Should Do)

### Phase 1: Basic Q CLI Integration
- [ ] Enable Q CLI debug logging: `export Q_LOG_LEVEL=trace`
- [ ] Study existing working MCP servers in Q CLI
- [ ] Create minimal server that only handles `initialize`
- [ ] Test ONLY in Q CLI context: `q mcp add --name test --command "server.py"`
- [ ] Verify server loads without "Transport closed" error

### Phase 2: Protocol Compliance  
- [ ] Study Q CLI MCP transport mechanism (not stdio)
- [ ] Implement proper transport layer
- [ ] Add server-side logging for all Q CLI interactions
- [ ] Test `initialize` → `tools/list` → `tools/call` sequence
- [ ] Verify JSON-RPC responses match Q CLI expectations

### Phase 3: Functionality Testing
- [ ] Add one tool at a time
- [ ] Test each tool in Q CLI after adding
- [ ] Verify tool responses display correctly in Q CLI
- [ ] Test error handling in Q CLI context
- [ ] Verify server stability during Q CLI sessions

### Phase 4: Production Readiness
- [ ] Load testing with multiple Q CLI sessions
- [ ] Error recovery testing
- [ ] Performance benchmarking in Q CLI
- [ ] Documentation for Q CLI MCP development
- [ ] Automated Q CLI integration tests

## 🔍 Debug Commands

```bash
# Enable Q CLI debugging
export Q_LOG_LEVEL=trace

# Check Q CLI logs
find /tmp -name "*qlog*" -o -name "*qchat*" 2>/dev/null
tail -f /tmp/qlog/qchat.log

# List working MCP servers
q mcp list

# Test MCP server loading
q mcp add --name test-server --command "/path/to/server.py"

# Remove failed server
q mcp remove --name test-server
```

## 🚨 Red Flags (Stop Development)
- "Transport closed" errors
- Server loads but tools don't work in Q CLI
- Manual testing works but Q CLI fails
- No visibility into Q CLI interactions
- Adding features before basic connection works

## ✅ Green Flags (Continue Development)  
- Server loads in Q CLI without errors
- Tools list appears in Q CLI
- Tool calls work and display results
- Server remains stable during Q CLI use
- Comprehensive logging shows all interactions

---
**Created**: 2025-09-21 03:15:48 UTC-07:00  
**Purpose**: Prevent future MCP development failures
