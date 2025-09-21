#!/usr/bin/env python3
"""
Phase 3 MCP Admin Server
- Agent Management
- System Administration
- Future Thinking Control
"""

import asyncio
import json
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import Tool, TextContent
from core_architecture import phase3_core, AgentConfig, ThinkingMode, InferenceRequest

app = Server("phase3-admin")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="create_agent",
            description="Create a new AI agent with future thinking capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Agent name"},
                    "model": {"type": "string", "description": "Model to use"},
                    "thinking_mode": {"type": "string", "enum": ["immediate", "future", "strategic"]},
                    "tools": {"type": "array", "items": {"type": "string"}},
                    "system_prompt": {"type": "string", "description": "System prompt for agent"}
                },
                "required": ["name", "model", "thinking_mode", "system_prompt"]
            }
        ),
        Tool(
            name="list_agents",
            description="List all available agents",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="delete_agent",
            description="Delete an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Agent name to delete"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="inference_with_thinking",
            description="Run inference with advanced thinking modes",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Input prompt"},
                    "agent_id": {"type": "string", "description": "Agent to use"},
                    "thinking_mode": {"type": "string", "enum": ["immediate", "future", "strategic"]},
                    "max_tokens": {"type": "integer", "default": 1000},
                    "temperature": {"type": "number", "default": 0.7}
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="get_openapi_spec",
            description="Get OpenAPI specification for the inference engine",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="system_admin",
            description="System administration and monitoring",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["status", "metrics", "health_check"]},
                    "details": {"type": "boolean", "default": False}
                },
                "required": ["action"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    try:
        if name == "create_agent":
            config = AgentConfig(
                name=arguments["name"],
                model=arguments["model"],
                thinking_mode=ThinkingMode(arguments["thinking_mode"]),
                tools=arguments.get("tools", []),
                system_prompt=arguments["system_prompt"]
            )
            result = await phase3_core.admin.create_agent(config)
            return [TextContent(type="text", text=result)]
        
        elif name == "list_agents":
            agents = await phase3_core.admin.list_agents()
            return [TextContent(type="text", text=json.dumps(agents, indent=2))]
        
        elif name == "delete_agent":
            agent_name = arguments["name"]
            if agent_name in phase3_core.admin.agents:
                del phase3_core.admin.agents[agent_name]
                phase3_core.admin.system_status["agents_count"] = len(phase3_core.admin.agents)
                result = f"Agent {agent_name} deleted successfully"
            else:
                result = f"Agent {agent_name} not found"
            return [TextContent(type="text", text=result)]
        
        elif name == "inference_with_thinking":
            request = InferenceRequest(
                prompt=arguments["prompt"],
                agent_id=arguments.get("agent_id"),
                thinking_mode=ThinkingMode(arguments.get("thinking_mode", "immediate")),
                max_tokens=arguments.get("max_tokens", 1000),
                temperature=arguments.get("temperature", 0.7)
            )
            result = await phase3_core.inference(request)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_openapi_spec":
            spec = await phase3_core.get_openapi_spec()
            return [TextContent(type="text", text=json.dumps(spec, indent=2))]
        
        elif name == "system_admin":
            action = arguments["action"]
            details = arguments.get("details", False)
            
            if action == "status":
                status = await phase3_core.admin.get_system_status()
                if details:
                    status["agents"] = await phase3_core.admin.list_agents()
                return [TextContent(type="text", text=json.dumps(status, indent=2))]
            
            elif action == "health_check":
                health = {
                    "status": "healthy",
                    "components": {
                        "inference_engine": "operational",
                        "admin_interface": "operational",
                        "thinking_system": "operational"
                    },
                    "agents_active": len(phase3_core.admin.agents)
                }
                return [TextContent(type="text", text=json.dumps(health, indent=2))]
            
            elif action == "metrics":
                metrics = {
                    "total_agents": len(phase3_core.admin.agents),
                    "thinking_modes": {
                        "immediate": 0,
                        "future": 0,
                        "strategic": 0
                    },
                    "uptime": "operational"
                }
                # Count thinking modes
                for agent in phase3_core.admin.agents.values():
                    metrics["thinking_modes"][agent.config.thinking_mode.value] += 1
                
                return [TextContent(type="text", text=json.dumps(metrics, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
