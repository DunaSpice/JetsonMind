#!/usr/bin/env python3
"""
JetsonMind MCP Client Examples
Demonstrates all MCP tools with practical examples
"""

import asyncio
import json
from mcp_inference_enhanced import EnhancedJetsonMindMCP

class MCPClientExamples:
    """Example MCP client interactions"""
    
    def __init__(self):
        self.server = EnhancedJetsonMindMCP()
    
    async def run_examples(self):
        """Run comprehensive MCP client examples"""
        print("🚀 JetsonMind MCP Client Examples")
        print("=" * 60)
        
        examples = [
            ("Basic Text Generation", self.example_basic_generation),
            ("Thinking Modes", self.example_thinking_modes),
            ("Model Management", self.example_model_management),
            ("Memory Monitoring", self.example_memory_monitoring),
            ("Hot Swapping", self.example_hot_swapping),
            ("Batch Processing", self.example_batch_processing),
            ("Agent Sessions", self.example_agent_sessions),
            ("System Monitoring", self.example_system_monitoring),
        ]
        
        for name, example_func in examples:
            print(f"\n📋 {name}")
            print("-" * 40)
            await example_func()
    
    async def example_basic_generation(self):
        """Basic text generation examples"""
        examples = [
            {"prompt": "Hello world"},
            {"prompt": "Explain quantum computing", "max_tokens": 50},
            {"prompt": "Write a Python function", "temperature": 0.3}
        ]
        
        for i, args in enumerate(examples, 1):
            print(f"Example {i}: {args}")
            result = await self.call_tool("generate_text", args)
            response = json.loads(result[0].text)
            print(f"  → Model: {response['model']}")
            print(f"  → Response: {response['text'][:50]}...")
            print()
    
    async def example_thinking_modes(self):
        """Thinking modes demonstration"""
        modes = [
            ("immediate", "What's 2+2?"),
            ("strategic", "Plan a software project"),
            ("future", "What will AI look like in 2030?")
        ]
        
        for mode, prompt in modes:
            args = {"prompt": prompt, "thinking_mode": mode}
            print(f"Mode '{mode}': {prompt}")
            result = await self.call_tool("generate_text", args)
            response = json.loads(result[0].text)
            print(f"  → Model: {response['model']}")
            print(f"  → Mode: {response['thinking_mode']}")
            print(f"  → Response: {response['text'][:60]}...")
            print()
    
    async def example_model_management(self):
        """Model loading/unloading examples"""
        # List models
        print("Available Models:")
        result = await self.call_tool("list_models", {})
        models = json.loads(result[0].text)
        for name, info in models.items():
            print(f"  • {name}: {info['size_gb']}GB ({info['tier']})")
        print()
        
        # Load model
        print("Loading llama-7b to RAM:")
        result = await self.call_tool("manage_model_loading", {
            "action": "load", 
            "model_name": "llama-7b", 
            "force_tier": "RAM"
        })
        load_result = json.loads(result[0].text)
        print(f"  → Status: {load_result['status']}")
        print(f"  → Location: {load_result.get('location', 'N/A')}")
        print()
        
        # Check status
        print("Loading Status:")
        result = await self.call_tool("manage_model_loading", {"action": "status"})
        status = json.loads(result[0].text)
        loaded = status['jetsonmind']['loaded_models']
        print(f"  → Loaded models: {len(loaded)}")
        for name, info in loaded.items():
            print(f"    • {name}: {info['location']} ({info['size_gb']}GB)")
    
    async def example_memory_monitoring(self):
        """Memory monitoring examples"""
        result = await self.call_tool("get_memory_status", {})
        status = json.loads(result[0].text)
        
        system = status['system']
        jetsonmind = status['jetsonmind']
        
        print("System Memory:")
        print(f"  • RAM: {system['ram_available_gb']:.1f}GB available / {system['ram_total_gb']:.1f}GB total")
        print(f"  • SWAP: {system['swap_used_gb']:.1f}GB used / {system['swap_total_gb']:.1f}GB total")
        print()
        
        print("JetsonMind Memory:")
        print(f"  • RAM: {jetsonmind['ram_used_gb']:.1f}GB / {jetsonmind['ram_limit_gb']:.1f}GB limit")
        print(f"  • SWAP: {jetsonmind['swap_used_gb']:.1f}GB / {jetsonmind['swap_limit_gb']:.1f}GB limit")
        print(f"  • Loaded models: {len(jetsonmind['loaded_models'])}")
    
    async def example_hot_swapping(self):
        """Hot swapping examples"""
        print("Hot Swapping gpt2-small → bert-large:")
        result = await self.call_tool("hot_swap_models", {
            "source_model": "gpt2-small",
            "target_model": "bert-large",
            "target_tier": "RAM"
        })
        swap_result = json.loads(result[0].text)
        print(f"  → Swap completed: {swap_result['hot_swap_completed']}")
        print(f"  → Unloaded: {swap_result['unloaded']['status']}")
        print(f"  → Loaded: {swap_result['loaded']['status']} to {swap_result['loaded'].get('location', 'N/A')}")
    
    async def example_batch_processing(self):
        """Batch processing examples"""
        prompts = [
            "What is AI?",
            "Explain machine learning",
            "Define neural networks"
        ]
        
        print(f"Batch processing {len(prompts)} prompts:")
        result = await self.call_tool("batch_inference", {
            "prompts": prompts,
            "thinking_mode": "immediate"
        })
        batch_result = json.loads(result[0].text)
        
        print(f"  → Processed: {batch_result['total_processed']} prompts")
        for i, result in enumerate(batch_result['batch_results'], 1):
            print(f"  → Result {i}: {result['text'][:40]}... (model: {result['model']})")
    
    async def example_agent_sessions(self):
        """Agent session examples"""
        session_id = "example_session_001"
        
        print(f"Creating agent session: {session_id}")
        result = await self.call_tool("create_agent_session", {
            "session_id": session_id,
            "model": "llama-7b",
            "system_prompt": "You are a helpful coding assistant."
        })
        print(f"  → {result[0].text}")
        
        # Generate with agent mode
        print("Agent conversation:")
        result = await self.call_tool("generate_text", {
            "prompt": "Help me write a Python function to sort a list",
            "agent_mode": True
        })
        response = json.loads(result[0].text)
        print(f"  → Model: {response['model']}")
        print(f"  → OpenAI format: {'choices' in response}")
    
    async def example_system_monitoring(self):
        """System monitoring examples"""
        result = await self.call_tool("get_system_status", {})
        status = json.loads(result[0].text)
        
        print("System Status:")
        print(f"  • Status: {status['status']}")
        print(f"  • Models available: {status['models_available']}")
        print(f"  • Models loaded: {status['models_loaded']}")
        print(f"  • Thinking modes: {', '.join(status['thinking_modes'])}")
        print(f"  • Agent compatible: {status['agent_compatible']}")
        print(f"  • Version: {status['version']}")
        
        # Get performance metrics
        result = await self.call_tool("get_performance_metrics", {})
        metrics = json.loads(result[0].text)
        
        print("\nPerformance Metrics:")
        print(f"  • Active models: {metrics['active_models']}")
        print(f"  • Total models: {metrics['total_models']}")
        print(f"  • Memory tiers: {metrics['memory_tiers']}")
    
    async def call_tool(self, name: str, arguments: dict):
        """Helper to call MCP tools"""
        return await self.server.app.call_tool(name, arguments)

async def main():
    """Run all MCP client examples"""
    examples = MCPClientExamples()
    await examples.run_examples()
    
    print("\n✅ All MCP Client Examples Complete!")
    print("\nFor more details, see:")
    print("  • MCP_CLIENT_GUIDE.md - Complete documentation")
    print("  • MCP_QUICK_REFERENCE.md - Quick reference card")

if __name__ == "__main__":
    asyncio.run(main())
