"""
MCP Router

Routes external requests to appropriate internal MCP servers based on
tool names and resource URIs.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger("mcp-router")

class MCPRouter:
    """Routes MCP requests to appropriate internal servers"""
    
    def __init__(self):
        self.tool_routing_table = self._build_tool_routing_table()
        self.resource_routing_table = self._build_resource_routing_table()
    
    def _build_tool_routing_table(self) -> Dict[str, str]:
        """Build routing table for tool calls"""
        return {
            # AI Tools
            'text_generate': 'ai',
            'image_analyze': 'ai',
            'audio_process': 'ai',
            'code_complete': 'ai',
            'multi_modal': 'ai',
            'chat_conversation': 'ai',
            
            # System Tools
            'get_system_status': 'system',
            'optimize_system': 'system',
            'restart_service': 'system',
            'update_configuration': 'system',
            'manage_processes': 'system',
            'monitor_resources': 'system',
            'get_performance_metrics': 'system',
            
            # Data Tools
            'list_models': 'data',
            'load_model': 'data',
            'unload_model': 'data',
            'cache_data': 'data',
            'get_cached_data': 'data',
            'cleanup_cache': 'data',
            'get_model_info': 'data',
            
            # Hardware Tools
            'get_hardware_info': 'hardware',
            'monitor_thermal': 'hardware',
            'control_power_mode': 'hardware',
            'get_gpu_status': 'hardware',
            'optimize_memory': 'hardware',
            'control_fan_speed': 'hardware',
            'get_jetson_stats': 'hardware'
        }
    
    def _build_resource_routing_table(self) -> Dict[str, str]:
        """Build routing table for resource access"""
        return {
            # Data Resources
            'jetson://models/': 'data',
            'jetson://cache/': 'data',
            'jetson://data/': 'data',
            
            # Hardware Resources
            'jetson://hardware/': 'hardware',
            'jetson://thermal/': 'hardware',
            'jetson://gpu/': 'hardware',
            'jetson://power/': 'hardware',
            
            # System Resources
            'jetson://system/': 'system',
            'jetson://performance/': 'system',
            'jetson://logs/': 'system'
        }
    
    def route_tool_call(self, tool_name: str) -> str:
        """
        Determine which internal server should handle this tool call.
        
        Args:
            tool_name (str): Name of the tool to execute
            
        Returns:
            str: Target server name ('ai', 'system', 'data', 'hardware')
        """
        target = self.tool_routing_table.get(tool_name, 'system')
        logger.debug(f"Routing tool '{tool_name}' to '{target}' server")
        return target
    
    def route_resource_read(self, uri: str) -> str:
        """
        Determine which internal server should handle this resource read.
        
        Args:
            uri (str): Resource URI to read
            
        Returns:
            str: Target server name
        """
        for prefix, server in self.resource_routing_table.items():
            if uri.startswith(prefix):
                logger.debug(f"Routing resource '{uri}' to '{server}' server")
                return server
        
        # Default to system server
        logger.debug(f"Routing resource '{uri}' to 'system' server (default)")
        return 'system'
    
    def get_server_for_tool(self, tool_name: str) -> Optional[str]:
        """Get server name for a specific tool (for debugging/info)"""
        return self.tool_routing_table.get(tool_name)
    
    def get_tools_for_server(self, server_name: str) -> list:
        """Get all tools handled by a specific server (for debugging/info)"""
        return [tool for tool, server in self.tool_routing_table.items() 
                if server == server_name]
