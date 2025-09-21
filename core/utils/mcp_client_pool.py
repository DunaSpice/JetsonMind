"""
MCP Client Pool

Manages connections to internal MCP servers and provides client instances
for the unified server to communicate with specialized servers.
"""

import asyncio
import logging
from typing import Dict, Optional
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

logger = logging.getLogger("mcp-client-pool")

class MCPClientPool:
    """Manages pool of MCP clients for internal server communication"""
    
    def __init__(self):
        self.clients: Dict[str, Client] = {}
        self.server_configs = {
            'ai': {
                'command': ['python3', 'internal/ai_mcp_server.py'],
                'description': 'AI inference and processing server'
            },
            'system': {
                'command': ['python3', 'internal/system_mcp_server.py'],
                'description': 'System management and monitoring server'
            },
            'data': {
                'command': ['python3', 'internal/data_mcp_server.py'],
                'description': 'Data and model management server'
            },
            'hardware': {
                'command': ['python3', 'internal/hardware_mcp_server.py'],
                'description': 'Hardware control and monitoring server'
            }
        }
    
    async def initialize(self):
        """Initialize connections to all internal MCP servers"""
        logger.info("Initializing internal MCP server connections")
        
        for server_name, config in self.server_configs.items():
            try:
                await self._connect_to_server(server_name, config)
                logger.info(f"Connected to {server_name} server: {config['description']}")
            except Exception as e:
                logger.error(f"Failed to connect to {server_name} server: {e}")
    
    async def _connect_to_server(self, server_name: str, config: dict):
        """Connect to a specific internal MCP server"""
        try:
            # Create MCP client with stdio transport
            client = Client(
                transport_type='stdio',
                command=config['command']
            )
            
            # Initialize the client connection
            await client.initialize()
            
            # Store the client
            self.clients[server_name] = client
            
        except Exception as e:
            logger.error(f"Error connecting to {server_name} server: {e}")
            raise
    
    async def get_client(self, server_name: str) -> ClientSession:
        """
        Get MCP client for specified internal server.
        
        Args:
            server_name (str): Name of internal server ('ai', 'system', 'data', 'hardware')
            
        Returns:
            Client: MCP client instance for the server
            
        Raises:
            ValueError: If server_name is not recognized
            ConnectionError: If client is not available
        """
        if server_name not in self.server_configs:
            raise ValueError(f"Unknown server: {server_name}")
        
        client = self.clients.get(server_name)
        if not client:
            # Try to reconnect
            logger.warning(f"Client for {server_name} not available, attempting reconnect")
            await self._connect_to_server(server_name, self.server_configs[server_name])
            client = self.clients.get(server_name)
            
            if not client:
                raise ConnectionError(f"Unable to connect to {server_name} server")
        
        return client
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all internal server connections.
        
        Returns:
            Dict[str, bool]: Health status for each server
        """
        health_status = {}
        
        for server_name in self.server_configs:
            try:
                client = self.clients.get(server_name)
                if client:
                    # Try a simple operation to test connectivity
                    await client.list_tools()
                    health_status[server_name] = True
                else:
                    health_status[server_name] = False
            except Exception as e:
                logger.warning(f"Health check failed for {server_name}: {e}")
                health_status[server_name] = False
        
        return health_status
    
    async def reconnect_server(self, server_name: str):
        """Reconnect to a specific internal server"""
        if server_name not in self.server_configs:
            raise ValueError(f"Unknown server: {server_name}")
        
        # Close existing connection if any
        if server_name in self.clients:
            try:
                await self.clients[server_name].close()
            except:
                pass
            del self.clients[server_name]
        
        # Reconnect
        await self._connect_to_server(server_name, self.server_configs[server_name])
        logger.info(f"Reconnected to {server_name} server")
    
    async def close_all(self):
        """Close all client connections"""
        logger.info("Closing all internal MCP client connections")
        
        for server_name, client in self.clients.items():
            try:
                await client.close()
                logger.debug(f"Closed connection to {server_name} server")
            except Exception as e:
                logger.warning(f"Error closing {server_name} client: {e}")
        
        self.clients.clear()
    
    def get_server_info(self) -> Dict[str, dict]:
        """Get information about all configured servers"""
        return {
            name: {
                'description': config['description'],
                'command': ' '.join(config['command']),
                'connected': name in self.clients
            }
            for name, config in self.server_configs.items()
        }
