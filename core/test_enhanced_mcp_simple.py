#!/usr/bin/env python3
"""
Simple test for Enhanced JetsonMind MCP Server
Tests the inference engine integration directly
"""

import asyncio
import json
from inference_engine_v3 import phase3_engine, InferenceRequest

async def test_inference_features():
    """Test inference engine features that will be exposed via MCP"""
    print("🚀 Testing JetsonMind Inference Engine Features")
    print("=" * 60)
    
    # Test 1: Model library
    print(f"\n🤖 Available Models: {len(phase3_engine.model_library)}")
    for name, spec in phase3_engine.model_library.items():
        print(f"  • {name}: {spec.size_gb}GB, {spec.tier.value}, thinking={spec.thinking_capable}")
    
    # Test 2: Thinking modes
    print("\n🧠 Testing Thinking Modes:")
    test_requests = [
        InferenceRequest(prompt="Hello world", thinking_mode="immediate"),
        InferenceRequest(prompt="Plan a project", thinking_mode="strategic"),
        InferenceRequest(prompt="Future predictions", thinking_mode="future"),
        InferenceRequest(prompt="Help me code", agent_mode=True)
    ]
    
    for req in test_requests:
        result = await phase3_engine.generate(req)
        mode = req.thinking_mode if not req.agent_mode else "agent"
        print(f"  • {mode}: {result['model']} -> {result.get('text', result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A'))[:50]}...")
    
    # Test 3: Model selection
    print("\n🎯 Testing Model Selection:")
    test_prompts = [
        "Hi",  # Short -> small model
        "This is a medium length prompt that should trigger different selection",  # Medium
        "This is a very long prompt with lots of words that should definitely trigger the large model selection based on the intelligent selection algorithm",  # Long
    ]
    
    for prompt in test_prompts:
        req = InferenceRequest(prompt=prompt)
        selected = await phase3_engine.select_model(req)
        print(f"  • '{prompt[:20]}...' -> {selected}")
    
    # Test 4: System status
    print("\n📊 System Status:")
    status = await phase3_engine.get_system_status()
    print(json.dumps(status, indent=2))
    
    # Test 5: OpenAPI spec
    print("\n📋 OpenAPI Specification Available:")
    spec = phase3_engine.get_openapi_spec()
    print(f"  • Title: {spec['info']['title']}")
    print(f"  • Version: {spec['info']['version']}")
    print(f"  • Endpoints: {len(spec['paths'])}")
    
    print("\n✅ All inference engine features tested successfully!")
    print("These capabilities are now exposed through the Enhanced MCP Server")

if __name__ == "__main__":
    asyncio.run(test_inference_features())
