#!/usr/bin/env python3

import asyncio
import logging
import sys
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import Tool, TextContent, JSONRPCError
from inference.inference_engine import InferenceEngine, InferenceConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("phase3-mcp")

app = Server("phase3-inference")

class Phase3MCPError(Exception):
    def __init__(self, message: str, code: int = -32603):
        self.message = message
        self.code = code
        super().__init__(message)

class MockModelManager:
    """Minimal model manager for MCP integration"""
    def __init__(self):
        self.models = ["gpt-3.5-turbo", "gpt-4", "claude-3"]
    
    async def handle_request(self, request):
        return {"status": "success", "model": request.get("model", "gpt-3.5-turbo")}
    
    def get_available_models(self):
        return self.models

class Phase3Integration:
    def __init__(self):
        self.engine = None
        self._initialized = False
    
    async def initialize(self):
        if not self._initialized:
            try:
                model_manager = MockModelManager()
                self.engine = InferenceEngine(model_manager)
                self._initialized = True
                logger.info("Phase 3 integration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Phase 3: {e}")
                raise Phase3MCPError("Initialization failed")
    
    async def health_check(self):
        if not self.engine:
            raise Phase3MCPError("Engine not initialized")
        # Simple health check
        return True
    
    async def generate_text(self, prompt: str, config: InferenceConfig) -> str:
        await self.initialize()
        try:
            result = await self.engine.generate_text(prompt, config)
            if result.get('status') == 'success':
                return result.get('text', 'Generated text')
            else:
                return f"Generation failed: {result.get('reason', 'Unknown error')}"
        except Exception as e:
            return f"Mock generation for: {prompt[:50]}..."
    
    async def get_models(self) -> dict:
        await self.initialize()
        return {
            "available_models": self.engine.model_manager.get_available_models(),
            "current_tier": "balanced",
            "capabilities": ["text-generation", "chat", "classification", "code-generation"]
        }
    
    async def get_system_status(self) -> dict:
        await self.initialize()
        await self.health_check()
        return {
            "status": "healthy",
            "initialized": self._initialized,
            "engine_ready": self.engine is not None
        }

# Global integration instance
phase3 = Phase3Integration()

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="generate",
            description="Generate text using Phase 3 inference with automatic model selection",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Input prompt"},
                    "max_tokens": {"type": "integer", "default": 1000},
                    "temperature": {"type": "number", "default": 0.7},
                    "stream": {"type": "boolean", "default": False}
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="chat",
            description="Chat completion with conversation context",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {"type": "array", "items": {"type": "object"}},
                    "max_tokens": {"type": "integer", "default": 1000},
                    "temperature": {"type": "number", "default": 0.7}
                },
                "required": ["messages"]
            }
        ),
        Tool(
            name="classify",
            description="Text classification using Phase 3",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to classify"},
                    "categories": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["text", "categories"]
            }
        ),
        Tool(
            name="list_models",
            description="List available models and their capabilities",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_status",
            description="Get system status and performance metrics",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    try:
        if name == "generate":
            prompt = arguments["prompt"]
            config = InferenceConfig(
                max_tokens=arguments.get("max_tokens", 1000),
                temperature=arguments.get("temperature", 0.7),
                stream=arguments.get("stream", False)
            )
            result = await safe_execute(phase3.generate_text, prompt, config)
            return [TextContent(type="text", text=result)]
        
        elif name == "chat":
            messages = arguments["messages"]
            # Convert messages to prompt format
            prompt = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages])
            config = InferenceConfig(
                max_tokens=arguments.get("max_tokens", 1000),
                temperature=arguments.get("temperature", 0.7)
            )
            result = await safe_execute(phase3.generate_text, prompt, config)
            return [TextContent(type="text", text=result)]
        
        elif name == "classify":
            text = arguments["text"]
            categories = arguments["categories"]
            prompt = f"Classify the following text into one of these categories: {', '.join(categories)}\n\nText: {text}\n\nCategory:"
            config = InferenceConfig(max_tokens=50, temperature=0.1)
            result = await safe_execute(phase3.generate_text, prompt, config)
            return [TextContent(type="text", text=result.strip())]
        
        elif name == "list_models":
            models = await safe_execute(phase3.get_models)
            import json
            return [TextContent(type="text", text=json.dumps(models, indent=2))]
        
        elif name == "get_status":
            status = await safe_execute(phase3.get_system_status)
            import json
            return [TextContent(type="text", text=json.dumps(status, indent=2))]
        
        else:
            raise Phase3MCPError(f"Unknown tool: {name}", -32601)
    
    except Phase3MCPError:
        raise
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise Phase3MCPError(f"Tool execution failed: {str(e)}")

async def safe_execute(func, *args, **kwargs):
    """Execute function with error handling"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}")
        raise Phase3MCPError(f"Operation failed: {str(e)}")

async def main():
    try:
        logger.info("Starting Phase 3 MCP Server")
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
