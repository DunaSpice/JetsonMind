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
from model_manager import model_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jetsonmind-enhanced-mcp")

class EnhancedJetsonMindMCP:
    """Enhanced MCP server exposing full inference engine capabilities"""
    
    def __init__(self):
        self.app = Server("jetsonmind-enhanced")
        self.engine = phase3_engine
        self.model_manager = model_manager
        self._initialize_models()
        self.setup_tools()
    
    def _initialize_models(self):
        """Register all models with the model manager"""
        for name, spec in self.engine.model_library.items():
            self.model_manager.register_model(name, spec)
    
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
                    description="Advanced model loading/unloading with hot swapping and storage tiers",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["load", "unload", "status", "hot_swap"]},
                            "model_name": {"type": "string", "description": "Model to manage"},
                            "force_tier": {"type": "string", "enum": ["RAM", "SWAP", "STORAGE"], "description": "Force specific memory tier"},
                            "to_storage": {"type": "boolean", "description": "Cache to storage when unloading"}
                        },
                        "required": ["action"]
                    }
                ),
                
                Tool(
                    name="get_memory_status",
                    description="Get detailed memory usage across RAM/SWAP/Storage tiers",
                    inputSchema={"type": "object", "properties": {}}
                ),
                
                Tool(
                    name="hot_swap_models",
                    description="Hot swap models between memory tiers for optimization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_model": {"type": "string", "description": "Model to swap out"},
                            "target_model": {"type": "string", "description": "Model to swap in"},
                            "target_tier": {"type": "string", "enum": ["RAM", "SWAP", "STORAGE"]}
                        },
                        "required": ["source_model", "target_model"]
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
                    force_tier = arguments.get("force_tier")
                    to_storage = arguments.get("to_storage", False)
                    
                    if action == "status":
                        status = self.model_manager.get_memory_status()
                        return [TextContent(type="text", text=json.dumps(status, indent=2))]
                    
                    elif action == "load" and model_name:
                        result = await self.model_manager.load_model(model_name, force_tier)
                        return [TextContent(type="text", text=json.dumps(result, indent=2))]
                    
                    elif action == "unload" and model_name:
                        result = await self.model_manager.unload_model(model_name, to_storage)
                        return [TextContent(type="text", text=json.dumps(result, indent=2))]
                    
                    elif action == "hot_swap":
                        # Hot swap: unload one, load another
                        if model_name:
                            unload_result = await self.model_manager.unload_model(model_name, to_storage=True)
                            # Could load another model here
                            return [TextContent(type="text", text=json.dumps(unload_result, indent=2))]
                
                elif name == "get_memory_status":
                    status = self.model_manager.get_memory_status()
                    return [TextContent(type="text", text=json.dumps(status, indent=2))]
                
                elif name == "hot_swap_models":
                    source_model = arguments["source_model"]
                    target_model = arguments["target_model"]
                    target_tier = arguments.get("target_tier")
                    
                    # Unload source model to storage
                    unload_result = await self.model_manager.unload_model(source_model, to_storage=True)
                    
                    # Load target model
                    load_result = await self.model_manager.load_model(target_model, target_tier)
                    
                    swap_result = {
                        "hot_swap_completed": True,
                        "unloaded": unload_result,
                        "loaded": load_result
                    }
                    return [TextContent(type="text", text=json.dumps(swap_result, indent=2))]
                
                elif name == "optimize_memory":
                    strategy = arguments.get("strategy", "balanced")
                    result = await self.model_manager.optimize_memory(strategy)
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
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
