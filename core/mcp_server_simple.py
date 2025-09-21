#!/usr/bin/env python3
import asyncio
import json
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
    return [TextContent(type="text", text="🤖 JetsonMind: gpt2-small, gpt-j-6b, llama-7b")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, {})

if __name__ == "__main__":
    asyncio.run(main())
