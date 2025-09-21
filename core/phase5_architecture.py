#!/usr/bin/env python3
"""
Phase 5: Intelligent AI Architecture
Optimized for TTS, STT, LLMs, Coding, OS tasks with MCP/Tool focus
"""

class Phase5ModelArchitecture:
    """Small footprint, large coverage AI powerhouse"""
    
    def __init__(self):
        self.model_tiers = {
            # Tier 1: Core Intelligence (Always Loaded)
            "core": {
                "phi-3-mini": {
                    "size": "2.3GB",
                    "capabilities": ["coding", "reasoning", "tool-use"],
                    "specialization": "MCP tool calling, code generation",
                    "priority": 1
                },
                "whisper-small": {
                    "size": "244MB", 
                    "capabilities": ["speech-to-text"],
                    "specialization": "Real-time STT, multilingual",
                    "priority": 1
                }
            },
            
            # Tier 2: Specialized Intelligence (Load on Demand)
            "specialized": {
                "codeqwen-1.5b": {
                    "size": "1.8GB",
                    "capabilities": ["coding", "debugging", "os-commands"],
                    "specialization": "System administration, shell scripting",
                    "priority": 2
                },
                "piper-tts": {
                    "size": "50MB",
                    "capabilities": ["text-to-speech"],
                    "specialization": "Fast, natural voice synthesis",
                    "priority": 2
                },
                "starcoder2-3b": {
                    "size": "3.2GB",
                    "capabilities": ["code-completion", "refactoring"],
                    "specialization": "Advanced coding assistance",
                    "priority": 2
                }
            },
            
            # Tier 3: Heavy Intelligence (Cloud/Swap when needed)
            "heavy": {
                "llama-3.2-3b": {
                    "size": "6.4GB",
                    "capabilities": ["reasoning", "general-intelligence"],
                    "specialization": "Complex problem solving",
                    "priority": 3
                },
                "whisper-medium": {
                    "size": "769MB",
                    "capabilities": ["high-accuracy-stt"],
                    "specialization": "Production STT quality",
                    "priority": 3
                }
            }
        }
        
        self.mcp_optimized_models = [
            "phi-3-mini",      # Best tool calling
            "codeqwen-1.5b",   # OS/system tasks
            "starcoder2-3b"    # Code generation
        ]
        
    def get_optimal_config(self, jetson_model="orin-nx"):
        """Get optimal model configuration for Jetson device"""
        configs = {
            "orin-nx": {
                "ram": "16GB",
                "core_models": ["phi-3-mini", "whisper-small", "piper-tts"],
                "specialized_models": ["codeqwen-1.5b", "starcoder2-3b"],
                "concurrent_limit": 3
            },
            "orin-nano": {
                "ram": "8GB", 
                "core_models": ["phi-3-mini", "whisper-small"],
                "specialized_models": ["codeqwen-1.5b"],
                "concurrent_limit": 2
            },
            "xavier-nx": {
                "ram": "8GB",
                "core_models": ["phi-3-mini", "whisper-small"],
                "specialized_models": ["piper-tts"],
                "concurrent_limit": 2
            }
        }
        return configs.get(jetson_model, configs["orin-nx"])

    def get_task_routing(self):
        """Route tasks to optimal models"""
        return {
            "tts": ["piper-tts"],
            "stt": ["whisper-small", "whisper-medium"],
            "coding": ["phi-3-mini", "codeqwen-1.5b", "starcoder2-3b"],
            "reasoning": ["phi-3-mini", "llama-3.2-3b"],
            "os-tasks": ["codeqwen-1.5b", "phi-3-mini"],
            "mcp-tools": ["phi-3-mini", "codeqwen-1.5b"],
            "general": ["phi-3-mini", "llama-3.2-3b"]
        }

if __name__ == "__main__":
    arch = Phase5ModelArchitecture()
    config = arch.get_optimal_config("orin-nx")
    print("🚀 Phase 5 Architecture Ready")
    print(f"Core Models: {config['core_models']}")
    print(f"Specialized: {config['specialized_models']}")
    print(f"Concurrent Limit: {config['concurrent_limit']}")
