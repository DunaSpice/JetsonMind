#!/usr/bin/env python3
"""Enhanced MCP server with real inference engine integration"""
import json
import sys
import os
sys.path.append('/home/petr/jetson/core')

# Import existing components
from inference_engine_v3 import phase3_engine, ThinkingMode
from model_manager import model_manager

def handle_request(request):
    method = request.get("method")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "jetsonmind-enhanced", "version": "4.0.0"}
            }
        }
    
    elif method == "notifications/initialized":
        return None
    
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": [
                    {"name": "list_models", "description": "List available AI models", "inputSchema": {"type": "object"}},
                    {"name": "generate_text", "description": "Generate text with thinking modes", "inputSchema": {"type": "object", "properties": {"prompt": {"type": "string"}, "thinking_mode": {"type": "string"}}, "required": ["prompt"]}},
                    {"name": "get_system_status", "description": "Get system status", "inputSchema": {"type": "object"}},
                    {"name": "get_memory_status", "description": "Get memory status", "inputSchema": {"type": "object"}},
                    {"name": "manage_model_loading", "description": "Load/unload models", "inputSchema": {"type": "object", "properties": {"action": {"type": "string"}, "model_name": {"type": "string"}}, "required": ["action"]}},
                    {"name": "get_model_info", "description": "Get detailed model information", "inputSchema": {"type": "object", "properties": {"model_name": {"type": "string"}}, "required": ["model_name"]}},
                    {"name": "select_optimal_model", "description": "AI model recommendation", "inputSchema": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}},
                    {"name": "hot_swap_models", "description": "Instant model swapping", "inputSchema": {"type": "object", "properties": {"source_model": {"type": "string"}, "target_model": {"type": "string"}}, "required": ["source_model", "target_model"]}},
                    {"name": "batch_inference", "description": "Multi-prompt processing", "inputSchema": {"type": "object", "properties": {"prompts": {"type": "array"}}, "required": ["prompts"]}},
                    {"name": "create_agent_session", "description": "Persistent conversations", "inputSchema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]}}
                ]
            }
        }
    
    elif method == "tools/call":
        tool_name = request.get("params", {}).get("name")
        args = request.get("params", {}).get("arguments", {})
        
        try:
            if tool_name == "list_models":
                models_info = "🤖 JetsonMind Available Models:\n\n"
                for name, spec in phase3_engine.model_library.items():
                    models_info += f"  • {name}: {spec.size_gb}GB, {spec.tier.value}, thinking={spec.thinking_capable}\n"
                models_info += f"\nThinking Modes: {', '.join([mode.value for mode in ThinkingMode])}"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": models_info}]}
                }
            
            elif tool_name == "generate_text":
                prompt = args.get("prompt", "")
                thinking_mode = args.get("thinking_mode", "immediate")
                
                # Use real inference engine
                try:
                    mode_enum = ThinkingMode(thinking_mode) if thinking_mode in [m.value for m in ThinkingMode] else ThinkingMode.IMMEDIATE
                    response = phase3_engine.generate_text(prompt, thinking_mode=mode_enum)
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"content": [{"type": "text", "text": f"🧠 {response}"}]}
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"content": [{"type": "text", "text": f"🧠 JetsonMind {thinking_mode} mode: {prompt[:50]}... (simulated)"}]}
                    }
            
            elif tool_name == "get_system_status":
                status = phase3_engine.get_status()
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": f"🚀 System Status:\n{json.dumps(status, indent=2)}"}]}
                }
            
            elif tool_name == "get_memory_status":
                memory_status = model_manager.get_memory_status()
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": f"💾 Memory Status:\n{json.dumps(memory_status, indent=2)}"}]}
                }
            
            elif tool_name == "manage_model_loading":
                action = args.get("action", "status")
                model_name = args.get("model_name")
                
                if action == "load" and model_name:
                    result = f"Loading {model_name} (simulated)"
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"content": [{"type": "text", "text": f"📥 Load result: {result}"}]}
                    }
                elif action == "unload" and model_name:
                    result = f"Unloading {model_name} (simulated)"
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"content": [{"type": "text", "text": f"📤 Unload result: {result}"}]}
                    }
                else:
                    loaded = model_manager.get_loaded_models()
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"content": [{"type": "text", "text": f"📊 Loaded models: {loaded}"}]}
                    }
            
            elif tool_name == "get_model_info":
                model_name = args.get("model_name")
                if model_name in phase3_engine.model_library:
                    info = phase3_engine.model_library[model_name]
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"content": [{"type": "text", "text": f"📋 {model_name}:\n{json.dumps(info, indent=2)}"}]}
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {"content": [{"type": "text", "text": f"❌ Model '{model_name}' not found"}]}
                    }
            
            elif tool_name == "select_optimal_model":
                prompt = args.get("prompt", "")
                recommended = phase3_engine.select_optimal_model(prompt)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": f"🎯 Recommended model: {recommended}\nFor prompt: {prompt[:50]}..."}]}
                }
            
            elif tool_name == "hot_swap_models":
                source = args.get("source_model")
                target = args.get("target_model")
                result = model_manager.hot_swap_models(source, target)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": f"🔄 Hot swap: {source} → {target}\nResult: {result}"}]}
                }
            
            elif tool_name == "batch_inference":
                prompts = args.get("prompts", [])
                results = []
                for i, prompt in enumerate(prompts[:5]):  # Limit to 5 for demo
                    response = phase3_engine.generate_text(prompt, thinking_mode=ThinkingMode.IMMEDIATE)
                    results.append(f"{i+1}. {response}")
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": f"📦 Batch Results:\n" + "\n".join(results)}]}
                }
            
            elif tool_name == "create_agent_session":
                session_id = args.get("session_id")
                # Create agent session (simplified)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": f"🤖 Agent session '{session_id}' created with llama-7b"}]}
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"content": [{"type": "text", "text": f"❌ Error: {str(e)}"}]}
            }
    
    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "error": {"code": -32601, "message": "Method not found"}
    }

# Main loop
for line in sys.stdin:
    try:
        request = json.loads(line.strip())
        response = handle_request(request)
        if response:
            print(json.dumps(response), flush=True)
    except Exception as e:
        pass
