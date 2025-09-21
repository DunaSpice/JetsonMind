#!/usr/bin/env python3
"""Minimal MCP Server using FastMCP pattern"""

from mcp.server.fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("jetson-minimal")

@mcp.tool()
def ping() -> str:
    """Test tool that returns pong"""
    return "pong"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
