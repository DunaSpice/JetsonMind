#!/usr/bin/env python3
"""
Minimal Working JetsonMind MCP Server
Fixed for Q CLI integration
"""

import asyncio
import logging
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jetsonmind-minimal")

# Create server
app = Server("jetsonmind-enhanced")

@app.list_tools()
def list_tools() -> List[Tool]:
    return [
        Tool(
            name="list_models",
            description="List available AI models",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="generate_text", 
            description="Generate text using JetsonMind models",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Input prompt"},
                    "model": {"type": "string", "description": "Model name (optional)"}
                },
                "required": ["prompt"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    if name == "list_models":
        models = {
            "gpt2-small": {"size": "0.5GB", "tier": "ram", "thinking": False},
            "gpt2-medium": {"size": "1.5GB", "tier": "ram", "thinking": False},
            "gpt2-large": {"size": "3.0GB", "tier": "ram", "thinking": False},
            "bert-large": {"size": "1.3GB", "tier": "ram", "thinking": False},
            "gpt-j-6b": {"size": "6.0GB", "tier": "swap", "thinking": True},
            "llama-7b": {"size": "7.0GB", "tier": "swap", "thinking": True}
        }
        
        result = "🤖 Available JetsonMind Models:\n"
        for name, config in models.items():
            result += f"  • {name}: {config['size']}, {config['tier']}, thinking={config['thinking']}\n"
        
        return [TextContent(type="text", text=result)]
    
    elif name == "generate_text":
        prompt = arguments.get("prompt", "")
        model = arguments.get("model", "gpt2-small")
        
        # Simulate text generation
        response = f"JetsonMind {model} response: {prompt[:50]}..."
        
        return [TextContent(type="text", text=response)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Start minimal MCP server"""
    try:
        logger.info("Starting Minimal JetsonMind MCP Server")
        
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream, 
                write_stream, 
                app.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
