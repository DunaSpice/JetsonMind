#!/usr/bin/env python3
"""MCP Client to call other MCP servers from JetsonMind"""
import subprocess
import json
import asyncio

class MCPClient:
    """Simple MCP client to call other MCP servers"""
    
    def __init__(self, server_command, server_args):
        self.server_command = server_command
        self.server_args = server_args
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """Call a tool on the MCP server"""
        try:
            # Initialize connection
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "jetsonmind", "version": "1.0"}
                },
                "id": 1
            }
            
            # Tool call request
            tool_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 2
            }
            
            # Send requests
            input_data = json.dumps(init_request) + "\n" + json.dumps(tool_request) + "\n"
            
            process = await asyncio.create_subprocess_exec(
                self.server_command, *self.server_args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input_data.encode())
            
            if process.returncode == 0:
                lines = stdout.decode().strip().split('\n')
                if len(lines) >= 2:
                    tool_response = json.loads(lines[1])
                    if 'result' in tool_response:
                        return tool_response['result']
            
            return {"error": f"MCP call failed: {stderr.decode()}"}
            
        except Exception as e:
            return {"error": f"MCP client error: {str(e)}"}
    
    async def search_and_call_space(self, query: str, input_text: str):
        """Search for a space and call it with input"""
        try:
            # First search for appropriate space
            search_result = await self.call_tool("search-spaces", {"query": query})
            
            if "error" in search_result:
                return search_result
            
            # Extract first space ID from search results
            content = search_result.get('content', [{}])[0].get('text', '')
            if 'glt3953/app-text_generation_chatglm2-6b' in content:
                # Use the found text generation space
                space_id = "glt3953/app-text_generation_chatglm2-6b"
                
                # Call the space (try common endpoint patterns)
                for endpoint in ["infer", "predict", "generate"]:
                    try:
                        result = await self.call_tool(f"{space_id.replace('/', '_')}-{endpoint}", {
                            "input": input_text,
                            "text": input_text,
                            "prompt": input_text
                        })
                        if "error" not in result:
                            return result
                    except:
                        continue
            
            return {"error": "No suitable text generation space found"}
            
        except Exception as e:
            return {"error": f"Search and call error: {str(e)}"}

# HuggingFace MCP client instance (official)
hf_mcp_client = MCPClient("npx", ["huggingface-mcp-server"])
