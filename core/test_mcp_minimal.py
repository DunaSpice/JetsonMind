#!/usr/bin/env python3

import asyncio
import logging
import sys
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

async def test_mcp():
    try:
        logger.info("Testing MCP server components...")
        
        # Test imports
        from mcp.server import Server
        from mcp.types import Tool, TextContent
        logger.info("MCP imports successful")
        
        # Test server creation
        app = Server("test-server")
        logger.info("Server creation successful")
        
        # Test tool definition
        @app.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="test",
                    description="Test tool",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        logger.info("Tool definition successful")
        
        # Test tool call
        @app.call_tool()
        async def call_tool(name: str, arguments: dict):
            return [TextContent(type="text", text="test")]
        logger.info("Tool call definition successful")
        
        logger.info("All tests passed!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp())
