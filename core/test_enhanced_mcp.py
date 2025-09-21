#!/usr/bin/env python3
"""
Test Enhanced JetsonMind MCP Server
Validates all advanced inference engine capabilities through MCP
"""

import asyncio
import json
from mcp_inference_enhanced import EnhancedJetsonMindMCP

async def test_enhanced_mcp():
    """Test all enhanced MCP capabilities"""
    print("🚀 Testing Enhanced JetsonMind MCP Server")
    print("=" * 60)
    
    server = EnhancedJetsonMindMCP()
    
    # Test 1: List all tools
    print("\n📋 Available Tools:")
    tools = await server.app.list_tools()
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")
    
    # Test 2: Model management
    print(f"\n🤖 Total Tools Available: {len(tools)}")
    
    # Test 3: Generate text with different thinking modes
    test_cases = [
        {
            "name": "Immediate Mode",
            "args": {"prompt": "Hello world", "thinking_mode": "immediate"}
        },
        {
            "name": "Strategic Mode", 
            "args": {"prompt": "Plan a software project", "thinking_mode": "strategic"}
        },
        {
            "name": "Future Mode",
            "args": {"prompt": "What will AI look like in 2030?", "thinking_mode": "future"}
        },
        {
            "name": "Agent Mode",
            "args": {"prompt": "Help me code", "agent_mode": True}
        }
    ]
    
    print("\n🧠 Testing Thinking Modes:")
    for test in test_cases:
        print(f"\n  {test['name']}:")
        result = await server.app.call_tool("generate_text", test["args"])
        response = json.loads(result[0].text)
        print(f"    Model: {response.get('model')}")
        print(f"    Mode: {response.get('thinking_mode', 'agent' if test['args'].get('agent_mode') else 'N/A')}")
    
    # Test 4: Model selection
    print("\n🎯 Testing Model Selection:")
    result = await server.app.call_tool("select_optimal_model", {
        "prompt": "Complex reasoning task requiring deep thinking",
        "thinking_mode": "strategic"
    })
    recommendation = json.loads(result[0].text)
    print(f"  Recommended: {recommendation['recommended_model']}")
    print(f"  Reasoning: {recommendation['reasoning']}")
    
    # Test 5: System status
    print("\n📊 System Status:")
    result = await server.app.call_tool("get_system_status", {})
    status = json.loads(result[0].text)
    print(f"  Status: {status['status']}")
    print(f"  Models Available: {status['models_available']}")
    print(f"  Agent Compatible: {status['agent_compatible']}")
    
    # Test 6: Batch processing
    print("\n⚡ Testing Batch Inference:")
    result = await server.app.call_tool("batch_inference", {
        "prompts": ["Hello", "How are you?", "Goodbye"],
        "thinking_mode": "immediate"
    })
    batch_result = json.loads(result[0].text)
    print(f"  Processed: {batch_result['total_processed']} prompts")
    
    # Test 7: Performance metrics
    print("\n📈 Performance Metrics:")
    result = await server.app.call_tool("get_performance_metrics", {})
    metrics = json.loads(result[0].text)
    print(f"  Active Models: {metrics['active_models']}")
    print(f"  Total Models: {metrics['total_models']}")
    print(f"  Memory Tiers: {metrics['memory_tiers']}")
    
    print("\n✅ Enhanced MCP Server Test Complete!")
    print("All advanced inference engine features are accessible through MCP")

if __name__ == "__main__":
    asyncio.run(test_enhanced_mcp())
