#!/usr/bin/env python3
"""
Phase 5 MCP Server - Intelligent AI Architecture
Optimized for TTS, STT, LLMs, Coding, OS tasks with MCP/Tool focus
"""

import json
import sys
import asyncio
from intelligent_model_manager import IntelligentModelManager, TaskType

class Phase5MCPServer:
    """MCP Server with intelligent model routing"""
    
    def __init__(self):
        self.model_manager = IntelligentModelManager()
        
    async def handle_request(self, request):
        """Handle MCP requests with intelligent routing"""
        method = request.get("method")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "jetsonmind-phase5",
                        "version": "5.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0", 
                "id": request.get("id"),
                "result": {
                    "tools": [
                        {"name": "intelligent_generate", "description": "Smart text generation with optimal model selection", "inputSchema": {"type": "object", "properties": {"prompt": {"type": "string"}, "task_type": {"type": "string"}}, "required": ["prompt"]}},
                        {"name": "speech_to_text", "description": "Convert speech to text using optimized STT models", "inputSchema": {"type": "object", "properties": {"audio_data": {"type": "string"}}, "required": ["audio_data"]}},
                        {"name": "text_to_speech", "description": "Convert text to speech using efficient TTS models", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
                        {"name": "code_assistant", "description": "Advanced coding assistance with specialized models", "inputSchema": {"type": "object", "properties": {"code_request": {"type": "string"}, "language": {"type": "string"}}, "required": ["code_request"]}},
                        {"name": "system_command", "description": "Execute system tasks with OS-optimized models", "inputSchema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
                        {"name": "mcp_tool_call", "description": "Optimized MCP tool calling with best models", "inputSchema": {"type": "object", "properties": {"tool_name": {"type": "string"}, "arguments": {"type": "object"}}, "required": ["tool_name"]}},
                        {"name": "get_model_status", "description": "View active models and resource usage", "inputSchema": {"type": "object", "properties": {}, "required": []}},
                        {"name": "optimize_models", "description": "Optimize model loading for current tasks", "inputSchema": {"type": "object", "properties": {"task_types": {"type": "array"}}, "required": ["task_types"]}}
                    ]
                }
            }
        
        elif method == "tools/call":
            return await self.handle_tool_call(request)
        
        return {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32601, "message": "Method not found"}}
    
    async def handle_tool_call(self, request):
        """Handle tool calls with intelligent model routing"""
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        try:
            if tool_name == "intelligent_generate":
                prompt = args.get("prompt", "")
                task_type_str = args.get("task_type", "general")
                
                # Map string to TaskType
                task_type_map = {
                    "coding": TaskType.CODING,
                    "reasoning": TaskType.REASONING,
                    "general": TaskType.GENERAL,
                    "mcp": TaskType.MCP_TOOLS,
                    "os": TaskType.OS_TASKS
                }
                task_type = task_type_map.get(task_type_str, TaskType.GENERAL)
                
                result = await self.model_manager.process_task(task_type, prompt)
                return self._success_response(request, result)
            
            elif tool_name == "speech_to_text":
                audio_data = args.get("audio_data", "")
                result = await self.model_manager.process_task(TaskType.STT, f"Audio: {audio_data}")
                return self._success_response(request, result)
            
            elif tool_name == "text_to_speech":
                text = args.get("text", "")
                result = await self.model_manager.process_task(TaskType.TTS, text)
                return self._success_response(request, result)
            
            elif tool_name == "code_assistant":
                code_request = args.get("code_request", "")
                language = args.get("language", "python")
                result = await self.model_manager.process_task(TaskType.CODING, f"{language}: {code_request}")
                return self._success_response(request, result)
            
            elif tool_name == "system_command":
                command = args.get("command", "")
                result = await self.model_manager.process_task(TaskType.OS_TASKS, command)
                return self._success_response(request, result)
            
            elif tool_name == "mcp_tool_call":
                tool_name_arg = args.get("tool_name", "")
                arguments = args.get("arguments", {})
                result = await self.model_manager.process_task(TaskType.MCP_TOOLS, f"Tool: {tool_name_arg}")
                return self._success_response(request, result)
            
            elif tool_name == "get_model_status":
                status = {
                    "active_models": list(self.model_manager.active_models.keys()),
                    "memory_usage": f"{self.model_manager.resource_monitor.get_available_memory_mb()}MB available",
                    "temperature": f"{self.model_manager.resource_monitor.get_temperature()}°C"
                }
                return self._success_response(request, f"📊 Model Status:\n{json.dumps(status, indent=2)}")
            
            elif tool_name == "optimize_models":
                task_types = args.get("task_types", [])
                # Pre-load optimal models for specified tasks
                results = []
                for task_str in task_types:
                    task_type_map = {
                        "coding": TaskType.CODING,
                        "tts": TaskType.TTS,
                        "stt": TaskType.STT,
                        "reasoning": TaskType.REASONING,
                        "os": TaskType.OS_TASKS,
                        "mcp": TaskType.MCP_TOOLS
                    }
                    if task_str in task_type_map:
                        task_type = task_type_map[task_str]
                        model_name = await self.model_manager.select_optimal_model(task_type)
                        await self.model_manager.ensure_model_loaded(model_name)
                        results.append(f"✅ Optimized for {task_str}: {model_name}")
                
                return self._success_response(request, f"🚀 Model Optimization:\n" + "\n".join(results))
            
            else:
                return self._error_response(request, f"Unknown tool: {tool_name}")
                
        except Exception as e:
            return self._error_response(request, f"Tool execution error: {str(e)}")
    
    def _success_response(self, request, content):
        """Create successful response"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {"content": [{"type": "text", "text": content}]}
        }
    
    def _error_response(self, request, message):
        """Create error response"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32000, "message": message}
        }

async def main():
    """Main MCP server loop"""
    server = Phase5MCPServer()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
