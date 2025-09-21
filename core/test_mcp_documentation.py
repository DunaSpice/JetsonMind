#!/usr/bin/env python3
"""
Test MCP Documentation Examples
Validates that all documented examples work correctly
"""

import asyncio
import json
from inference_engine_v3 import phase3_engine, InferenceRequest
from model_manager import model_manager

async def test_documentation_examples():
    """Test all examples from the documentation"""
    print("📚 Testing MCP Documentation Examples")
    print("=" * 60)
    
    # Initialize model manager
    for name, spec in phase3_engine.model_library.items():
        model_manager.register_model(name, spec)
    
    # Test 1: Basic text generation examples
    print("\n🚀 Basic Text Generation Examples:")
    examples = [
        {"prompt": "Hello world"},
        {"prompt": "Explain quantum computing", "thinking_mode": "strategic"},
        {"prompt": "Help me debug code", "agent_mode": True}
    ]
    
    for i, args in enumerate(examples, 1):
        print(f"  Example {i}: {args}")
        if args.get("agent_mode"):
            req = InferenceRequest(prompt=args["prompt"], agent_mode=True)
        else:
            req = InferenceRequest(
                prompt=args["prompt"], 
                thinking_mode=args.get("thinking_mode", "immediate")
            )
        result = await phase3_engine.generate(req)
        print(f"    → Model: {result.get('model', 'N/A')}")
        print(f"    → Response: {str(result.get('text', result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')))[:40]}...")
    
    # Test 2: Model management examples
    print("\n🤖 Model Management Examples:")
    
    # List models
    print("  Available Models:")
    for name, spec in phase3_engine.model_library.items():
        print(f"    • {name}: {spec.size_gb}GB ({spec.tier.value}) - thinking: {spec.thinking_capable}")
    
    # Load model
    print("  Loading llama-7b to RAM:")
    result = await model_manager.load_model("llama-7b", "RAM")
    print(f"    → Status: {result['status']}")
    print(f"    → Location: {result.get('location', 'N/A')}")
    
    # Memory status
    print("  Memory Status:")
    status = model_manager.get_memory_status()
    jetsonmind = status['jetsonmind']
    print(f"    → RAM: {jetsonmind['ram_used_gb']:.1f}GB / {jetsonmind['ram_limit_gb']:.1f}GB")
    print(f"    → SWAP: {jetsonmind['swap_used_gb']:.1f}GB / {jetsonmind['swap_limit_gb']:.1f}GB")
    print(f"    → Loaded models: {len(jetsonmind['loaded_models'])}")
    
    # Test 3: Thinking modes
    print("\n🧠 Thinking Modes Examples:")
    modes = [
        ("immediate", "What's 2+2?"),
        ("strategic", "Plan a software project"),
        ("future", "What will AI look like in 2030?")
    ]
    
    for mode, prompt in modes:
        req = InferenceRequest(prompt=prompt, thinking_mode=mode)
        result = await phase3_engine.generate(req)
        print(f"  {mode}: {result['model']} → {result['text'][:50]}...")
    
    # Test 4: Model selection
    print("\n🎯 Model Selection Examples:")
    selection_tests = [
        ("Short prompt", "Hi"),
        ("Complex reasoning", "Analyze the implications of quantum computing", "strategic"),
        ("Agent task", "Help me debug code", "immediate", True)
    ]
    
    for name, prompt, *args in selection_tests:
        thinking_mode = args[0] if args else "immediate"
        agent_mode = args[1] if len(args) > 1 else False
        
        req = InferenceRequest(prompt=prompt, thinking_mode=thinking_mode, agent_mode=agent_mode)
        selected = await phase3_engine.select_model(req)
        print(f"  {name}: {selected}")
    
    # Test 5: Hot swapping
    print("\n🔄 Hot Swapping Example:")
    # Unload a model
    unload_result = await model_manager.unload_model("llama-7b", to_storage=True)
    print(f"  Unloaded llama-7b: {unload_result['status']}")
    
    # Load different model
    load_result = await model_manager.load_model("bert-large", "RAM")
    print(f"  Loaded bert-large: {load_result['status']} → {load_result.get('location')}")
    
    # Test 6: Batch processing simulation
    print("\n⚡ Batch Processing Example:")
    prompts = ["What is AI?", "Explain ML", "Define neural networks"]
    results = []
    
    for prompt in prompts:
        req = InferenceRequest(prompt=prompt, thinking_mode="immediate")
        result = await phase3_engine.generate(req)
        results.append(result)
    
    print(f"  Processed {len(results)} prompts:")
    for i, result in enumerate(results, 1):
        print(f"    {i}. {result['model']}: {result['text'][:30]}...")
    
    # Test 7: System status
    print("\n📊 System Status Example:")
    status = await phase3_engine.get_system_status()
    print(f"  Status: {status['status']}")
    print(f"  Models available: {status['models_available']}")
    print(f"  Thinking modes: {len(status['thinking_modes'])}")
    print(f"  Agent compatible: {status['agent_compatible']}")
    
    # Test 8: Memory optimization
    print("\n⚡ Memory Optimization Example:")
    opt_result = await model_manager.optimize_memory("balanced")
    print(f"  Strategy: {opt_result['strategy']}")
    print(f"  Status: {opt_result.get('status', 'completed')}")
    
    print("\n✅ All Documentation Examples Tested Successfully!")
    print("\nDocumentation Files:")
    print("  • MCP_CLIENT_GUIDE.md - Complete tool documentation")
    print("  • MCP_QUICK_REFERENCE.md - Quick reference card")
    print("  • MCP_README.md - Integration overview")

if __name__ == "__main__":
    asyncio.run(test_documentation_examples())
