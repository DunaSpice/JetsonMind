#!/usr/bin/env python3

import asyncio
import json
import sys
from mcp.server.models import InitializationOptions
from mcp.server.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

server = Server("phase3-inference")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    return ListToolsResult(
        tools=[
            Tool(
                name="generate",
                description="Generate text using Phase 3 inference",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Input prompt"}
                    },
                    "required": ["prompt"]
                }
            ),
            Tool(
                name="get_status", 
                description="Get system status",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    try:
        if request.params.name == "generate":
            prompt = request.params.arguments.get("prompt", "")
            result = f"Mock generation for: {prompt[:50]}..."
            return CallToolResult(content=[TextContent(type="text", text=result)])
        
        elif request.params.name == "get_status":
            status = {"status": "healthy", "server": "phase3-inference"}
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(status, indent=2))])
        
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {request.params.name}")])
    
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="phase3-inference",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
