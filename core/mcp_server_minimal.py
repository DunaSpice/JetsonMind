#!/usr/bin/env python3
"""Ultra-minimal working MCP server"""
import asyncio
import sys
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("jetsonmind-enhanced")

@app.list_tools()
def list_tools():
    return [Tool(name="list_models", description="List JetsonMind models", inputSchema={"type": "object"})]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "list_models":
        return [TextContent(type="text", text="🤖 JetsonMind Models: gpt2-small, gpt2-medium, gpt-j-6b, llama-7b")]
    return [TextContent(type="text", text="Unknown tool")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
