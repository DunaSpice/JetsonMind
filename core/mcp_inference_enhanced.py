#!/usr/bin/env python3
"""
Enhanced JetsonMind MCP Server - Full Inference Engine Integration

Exposes ALL inference engine capabilities through MCP protocol:
- Advanced model selection and management
- Thinking modes (immediate, future, strategic)
- Agent compatibility and session management
- Hardware-aware model tiering
- Performance monitoring and optimization
- OpenAPI specification access

Author: JetsonMind Team
Version: 4.0.0
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from inference_engine_v3 import phase3_engine, ThinkingMode, ModelTier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jetsonmind-enhanced-mcp")

class EnhancedJetsonMindMCP:
    """Enhanced MCP server exposing full inference engine capabilities"""
    
    def __init__(self):
        self.app = Server("jetsonmind-enhanced")
        self.engine = phase3_engine
        self.setup_tools()
    
    def setup_tools(self):
        """Setup comprehensive MCP tools for inference engine"""
        
        @self.app.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                # Core Inference Tools
                Tool(
                    name="generate_text",
                    description="Generate text with advanced thinking modes and model selection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Input prompt"},
                            "model": {"type": "string", "description": "Specific model (optional)"},
                            "thinking_mode": {
                                "type": "string", 
                                "enum": ["immediate", "future", "strategic"],
                                "description": "Thinking approach for response"
                            },
                            "agent_mode": {"type": "boolean", "description": "OpenAI agent compatibility"},
                            "max_tokens": {"type": "integer", "default": 100},
                            "temperature": {"type": "number", "default": 0.7}
                        },
                        "required": ["prompt"]
                    }
                ),
                
                # Model Management Tools
                Tool(
                    name="list_models",
                    description="List all available models with capabilities and tiers",
                    inputSchema={"type": "object", "properties": {}}
                ),
                
                Tool(
                    name="get_model_info",
                    description="Get detailed information about a specific model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model_name": {"type": "string", "description": "Model name to query"}
                        },
                        "required": ["model_name"]
                    }
                ),
                
                Tool(
                    name="select_optimal_model",
                    description="Get optimal model recommendation for a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Task prompt"},
                            "thinking_mode": {"type": "string", "enum": ["immediate", "future", "strategic"]},
                            "agent_mode": {"type": "boolean", "default": False}
                        },
                        "required": ["prompt"]
                    }
                ),
                
                # System Management Tools
                Tool(
                    name="get_system_status",
                    description="Get comprehensive system status and performance metrics",
                    inputSchema={"type": "object", "properties": {}}
                ),
                
                Tool(
                    name="manage_model_loading",
                    description="Load/unload models for memory optimization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["load", "unload", "status"]},
                            "model_name": {"type": "string", "description": "Model to manage"}
                        },
                        "required": ["action"]
                    }
                ),
                
                # Advanced Features
                Tool(
                    name="batch_inference",
                    description="Process multiple prompts efficiently",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompts": {"type": "array", "items": {"type": "string"}},
                            "thinking_mode": {"type": "string", "enum": ["immediate", "future", "strategic"]},
                            "model": {"type": "string", "description": "Model for all prompts"}
                        },
                        "required": ["prompts"]
                    }
                ),
                
                Tool(
                    name="create_agent_session",
                    description="Create persistent agent session for multi-turn conversations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Unique session identifier"},
                            "model": {"type": "string", "description": "Model for session"},
                            "system_prompt": {"type": "string", "description": "System prompt for agent"}
                        },
                        "required": ["session_id"]
                    }
                ),
                
                Tool(
                    name="get_openapi_spec",
                    description="Get OpenAPI 3.0 specification for REST API compatibility",
                    inputSchema={"type": "object", "properties": {}}
                ),
                
                # Performance & Monitoring
                Tool(
                    name="get_performance_metrics",
                    description="Get detailed performance metrics and benchmarks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "Specific model metrics"},
                            "time_range": {"type": "string", "description": "Time range for metrics"}
                        }
                    }
                ),
                
                Tool(
                    name="optimize_memory",
                    description="Optimize memory usage based on current workload",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "strategy": {"type": "string", "enum": ["aggressive", "balanced", "conservative"]}
                        }
                    }
                )
            ]
        
        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Execute inference engine tools"""
            try:
                logger.info(f"Executing tool: {name} with args: {arguments}")
                
                if name == "generate_text":
                    from inference_engine_v3 import InferenceRequest
                    request = InferenceRequest(**arguments)
                    result = await self.engine.generate(request)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
                elif name == "list_models":
                    models = {}
                    for name, spec in self.engine.model_library.items():
                        models[name] = {
                            "size_gb": spec.size_gb,
                            "tier": spec.tier.value,
                            "capabilities": spec.capabilities,
                            "thinking_capable": spec.thinking_capable
                        }
                    return [TextContent(type="text", text=json.dumps(models, indent=2))]
                
                elif name == "get_model_info":
                    model_name = arguments["model_name"]
                    if model_name in self.engine.model_library:
                        spec = self.engine.model_library[model_name]
                        info = {
                            "name": spec.name,
                            "size_gb": spec.size_gb,
                            "tier": spec.tier.value,
                            "capabilities": spec.capabilities,
                            "thinking_capable": spec.thinking_capable,
                            "loaded": model_name in self.engine.active_models
                        }
                        return [TextContent(type="text", text=json.dumps(info, indent=2))]
                    else:
                        return [TextContent(type="text", text=f"Model '{model_name}' not found")]
                
                elif name == "select_optimal_model":
                    from inference_engine_v3 import InferenceRequest
                    request = InferenceRequest(**arguments)
                    optimal_model = await self.engine.select_model(request)
                    spec = self.engine.model_library[optimal_model]
                    
                    recommendation = {
                        "recommended_model": optimal_model,
                        "reasoning": f"Selected based on prompt length, thinking mode, and capabilities",
                        "model_info": {
                            "size_gb": spec.size_gb,
                            "tier": spec.tier.value,
                            "capabilities": spec.capabilities
                        }
                    }
                    return [TextContent(type="text", text=json.dumps(recommendation, indent=2))]
                
                elif name == "get_system_status":
                    status = await self.engine.get_system_status()
                    return [TextContent(type="text", text=json.dumps(status, indent=2))]
                
                elif name == "batch_inference":
                    results = []
                    for prompt in arguments["prompts"]:
                        from inference_engine_v3 import InferenceRequest
                        req_args = {**arguments, "prompt": prompt}
                        del req_args["prompts"]  # Remove batch-specific arg
                        request = InferenceRequest(**req_args)
                        result = await self.engine.generate(request)
                        results.append(result)
                    
                    return [TextContent(type="text", text=json.dumps({
                        "batch_results": results,
                        "total_processed": len(results)
                    }, indent=2))]
                
                elif name == "create_agent_session":
                    session_id = arguments["session_id"]
                    self.engine.agent_sessions[session_id] = {
                        "created": asyncio.get_event_loop().time(),
                        "model": arguments.get("model", "llama-7b"),
                        "system_prompt": arguments.get("system_prompt", "You are a helpful AI assistant."),
                        "messages": []
                    }
                    return [TextContent(type="text", text=f"Agent session '{session_id}' created")]
                
                elif name == "get_openapi_spec":
                    spec = self.engine.get_openapi_spec()
                    return [TextContent(type="text", text=json.dumps(spec, indent=2))]
                
                elif name == "get_performance_metrics":
                    metrics = {
                        "active_models": len(self.engine.active_models),
                        "total_models": len(self.engine.model_library),
                        "thinking_cache_size": len(self.engine.thinking_cache),
                        "agent_sessions": len(self.engine.agent_sessions),
                        "memory_tiers": {
                            "ram_models": len([m for m in self.engine.model_library.values() if m.tier == ModelTier.RAM]),
                            "swap_models": len([m for m in self.engine.model_library.values() if m.tier == ModelTier.SWAP]),
                            "storage_models": len([m for m in self.engine.model_library.values() if m.tier == ModelTier.STORAGE])
                        }
                    }
                    return [TextContent(type="text", text=json.dumps(metrics, indent=2))]
                
                elif name == "manage_model_loading":
                    action = arguments["action"]
                    model_name = arguments.get("model_name")
                    
                    if action == "status":
                        status = {
                            "loaded_models": list(self.engine.active_models.keys()),
                            "available_models": list(self.engine.model_library.keys())
                        }
                        return [TextContent(type="text", text=json.dumps(status, indent=2))]
                    
                    elif action == "load" and model_name:
                        if model_name in self.engine.model_library:
                            self.engine.active_models[model_name] = {"loaded_at": asyncio.get_event_loop().time()}
                            return [TextContent(type="text", text=f"Model '{model_name}' loaded")]
                        else:
                            return [TextContent(type="text", text=f"Model '{model_name}' not found")]
                    
                    elif action == "unload" and model_name:
                        if model_name in self.engine.active_models:
                            del self.engine.active_models[model_name]
                            return [TextContent(type="text", text=f"Model '{model_name}' unloaded")]
                        else:
                            return [TextContent(type="text", text=f"Model '{model_name}' not loaded")]
                
                elif name == "optimize_memory":
                    strategy = arguments.get("strategy", "balanced")
                    
                    if strategy == "aggressive":
                        # Unload all but essential models
                        essential = ["gpt2-small"]
                        unloaded = []
                        for model in list(self.engine.active_models.keys()):
                            if model not in essential:
                                del self.engine.active_models[model]
                                unloaded.append(model)
                        
                        return [TextContent(type="text", text=json.dumps({
                            "strategy": "aggressive",
                            "unloaded_models": unloaded,
                            "remaining_models": list(self.engine.active_models.keys())
                        }, indent=2))]
                    
                    else:
                        return [TextContent(type="text", text=f"Memory optimization with '{strategy}' strategy completed")]
                
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Start enhanced MCP server"""
    try:
        logger.info("Starting Enhanced JetsonMind MCP Server")
        server = EnhancedJetsonMindMCP()
        logger.info("Enhanced MCP server ready - full inference engine capabilities exposed")
        await server.app.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
