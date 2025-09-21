#!/usr/bin/env python3

import asyncio
import json
import subprocess
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_phase3_mcp():
    """Test Phase 3 MCP server integration"""
    
    print("🧪 Testing Phase 3 MCP Integration")
    print("=" * 40)
    
    server_params = StdioServerParameters(
        command="python3",
        args=["/home/petr/phase3/mcp_server.py"],
        env={"PYTHONPATH": "/home/petr/phase3"}
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                await session.initialize()
                
                # Test 1: List tools
                print("\n🔍 Testing: List Tools")
                tools = await session.list_tools()
                print(f"✅ Found {len(tools.tools)} tools: {[t.name for t in tools.tools]}")
                
                # Test 2: Get status
                print("\n🔍 Testing: System Status")
                result = await session.call_tool("get_status", {})
                print(f"✅ Status: {result.content[0].text[:100]}...")
                
                # Test 3: Simple generation
                print("\n🔍 Testing: Text Generation")
                result = await session.call_tool("generate", {
                    "prompt": "Hello, world!",
                    "max_tokens": 50
                })
                print(f"✅ Generated: {result.content[0].text[:100]}...")
                
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    print(f"\n🎉 Integration test complete!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_phase3_mcp())
    sys.exit(0 if success else 1)
