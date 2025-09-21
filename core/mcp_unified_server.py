#!/usr/bin/env python3
"""
JetsonMind Unified MCP Server

External-facing MCP server that provides a single interface to all JetsonMind
capabilities by internally coordinating with specialized MCP servers.

Architecture: MCP inside MCP
- External: Clients → MCP → Unified Server  
- Internal: Unified Server → MCP → Specialized Servers

Author: JetsonMind Team
Version: 2.0.0
Date: 2025-09-20
"""

import asyncio
import json
import logging
from typing import List, Dict, Any
from mcp.server import Server
from mcp.types import Tool, TextContent, Resource
from routing.mcp_router import MCPRouter
from utils.mcp_client_pool import MCPClientPool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jetsonmind-unified-mcp")

class JetsonMindUnifiedMCPServer:
    """
    Unified MCP server that aggregates capabilities from internal specialized servers.
    Provides single point of entry for all AI clients.
    """
    
    def __init__(self):
        self.app = Server("jetsonmind-unified")
        self.router = MCPRouter()
        self.internal_clients = MCPClientPool()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.app.list_tools()
        async def list_tools() -> List[Tool]:
            """
            Aggregate tools from all internal MCP servers.
            
            Returns:
                List[Tool]: Combined tools from AI, System, Data, and Hardware servers
            """
            try:
                logger.info("Aggregating tools from internal MCP servers")
                all_tools = []
                
                # Get tools from each internal server
                for server_name in ['ai', 'system', 'data', 'hardware']:
                    try:
                        client = await self.internal_clients.get_client(server_name)
                        tools = await client.list_tools()
                        all_tools.extend(tools.tools if hasattr(tools, 'tools') else tools)
                        logger.info(f"Added {len(tools)} tools from {server_name} server")
                    except Exception as e:
                        logger.warning(f"Failed to get tools from {server_name} server: {e}")
                
                logger.info(f"Total tools available: {len(all_tools)}")
                return all_tools
                
            except Exception as e:
                logger.error(f"Error aggregating tools: {e}")
                return []
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[TextContent]:
            """
            Route tool calls to appropriate internal MCP server.
            
            Args:
                name (str): Tool name to execute
                arguments (dict): Tool parameters
                
            Returns:
                List[TextContent]: Tool execution results
            """
            try:
                logger.info(f"Routing tool call: {name} with args: {arguments}")
                
                # Determine target server
                target_server = self.router.route_tool_call(name)
                logger.info(f"Routing {name} to {target_server} server")
                
                # Get client for target server
                client = await self.internal_clients.get_client(target_server)
                
                # Execute tool on internal server
                result = await client.call_tool(name, arguments)
                
                # Return result (ensure it's in correct format)
                if isinstance(result, list):
                    return result
                elif hasattr(result, 'content'):
                    return result.content
                else:
                    return [TextContent(type="text", text=str(result))]
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.app.list_resources()
        async def list_resources() -> List[Resource]:
            """
            Aggregate resources from internal MCP servers.
            
            Returns:
                List[Resource]: Combined resources from all internal servers
            """
            try:
                logger.info("Aggregating resources from internal MCP servers")
                all_resources = []
                
                # Get resources from servers that provide them
                for server_name in ['data', 'hardware']:
                    try:
                        client = await self.internal_clients.get_client(server_name)
                        resources = await client.list_resources()
                        all_resources.extend(resources.resources if hasattr(resources, 'resources') else resources)
                        logger.info(f"Added {len(resources)} resources from {server_name} server")
                    except Exception as e:
                        logger.warning(f"Failed to get resources from {server_name} server: {e}")
                
                logger.info(f"Total resources available: {len(all_resources)}")
                return all_resources
                
            except Exception as e:
                logger.error(f"Error aggregating resources: {e}")
                return []
        
        @self.app.read_resource()
        async def read_resource(uri: str) -> str:
            """
            Read resource from appropriate internal MCP server.
            
            Args:
                uri (str): Resource URI to read
                
            Returns:
                str: Resource content
            """
            try:
                logger.info(f"Reading resource: {uri}")
                
                # Determine target server based on URI
                target_server = self.router.route_resource_read(uri)
                logger.info(f"Routing resource {uri} to {target_server} server")
                
                # Get client and read resource
                client = await self.internal_clients.get_client(target_server)
                result = await client.read_resource(uri)
                
                return result.content if hasattr(result, 'content') else str(result)
                
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return f"Error: {str(e)}"

async def main():
    """
    Main server entry point.
    Starts the unified MCP server and internal server coordination.
    """
    try:
        logger.info("Starting JetsonMind Unified MCP Server")
        
        # Create unified server instance
        server = JetsonMindUnifiedMCPServer()
        
        # Initialize internal client connections
        await server.internal_clients.initialize()
        
        # Start the MCP server
        logger.info("Unified MCP server ready - accepting client connections")
        await server.app.run()
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("JetsonMind Unified MCP Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
