# Folder B: Agent Orchestration & Intelligence

## ✅ INTEGRATED WITH OPENAI AGENTS SDK

**Agent Server:** Running on port 8001
**Integration:** Connected to Folder A backend (port 8000)
**Tools:** Database query, conversation search, model selection

## Current Status
- ✅ OpenAI Agents SDK integration via Phase3Agent class
- ✅ Existing inference engine integrated for model selection
- ✅ MCP tools wrapped as agent functions
- ✅ FastAPI agent server running on port 8001
- ✅ Connected to Folder A database backend

## Available Endpoints
- `POST /chat` - Process messages through agent intelligence
- `GET /tools` - List available agent tools
- `GET /health` - Agent server health check

## Core Components
- `agents_core.py` - OpenAI Agents SDK integration
- `agent_server.py` - FastAPI server for agent processing
- `inference_engine.py` - Phase 1/2 model selection (existing)
- `mcp_server.py` - MCP tool integration (existing)

## Agent Capabilities
- **Context Awareness** - Uses conversation history from database
- **Model Selection** - Integrates existing inference engine
- **Tool Access** - Database queries, conversation search
- **Future Thinking** - Strategic analysis and multi-step reasoning

## Integration Points
- Consumes conversation data from Folder A API
- Provides intelligent responses for Folder C frontend
- Uses existing MCP postgres server for database access

## Next Steps for AI Engineer B
1. Add more sophisticated agent workflows
2. Implement function calling with OpenAI tools
3. Add memory management and context optimization
4. Create specialized agents for different tasks
