#!/usr/bin/env python3

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_all_tools():
    """Comprehensive test of all Phase 3 MCP tools"""
    
    print("🚀 Phase 3 MCP Server - Comprehensive Test")
    print("=" * 50)
    
    server_params = StdioServerParameters(
        command="python3",
        args=["/home/petr/phase3/mcp_server.py"],
        env={"PYTHONPATH": "/home/petr/phase3"}
    )
    
    tests_passed = 0
    tests_total = 0
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Test 1: List Tools
                print("\n🔧 Test 1: List Tools")
                tests_total += 1
                tools = await session.list_tools()
                expected_tools = {'generate', 'chat', 'classify', 'list_models', 'get_status'}
                actual_tools = {t.name for t in tools.tools}
                if expected_tools.issubset(actual_tools):
                    print(f"✅ All expected tools found: {sorted(actual_tools)}")
                    tests_passed += 1
                else:
                    print(f"❌ Missing tools: {expected_tools - actual_tools}")
                
                # Test 2: System Status
                print("\n💚 Test 2: System Status")
                tests_total += 1
                try:
                    result = await session.call_tool("get_status", {})
                    status = json.loads(result.content[0].text)
                    if status.get("status") == "healthy":
                        print(f"✅ System healthy: {status}")
                        tests_passed += 1
                    else:
                        print(f"❌ System not healthy: {status}")
                except Exception as e:
                    print(f"❌ Status check failed: {e}")
                
                # Test 3: List Models
                print("\n📋 Test 3: List Models")
                tests_total += 1
                try:
                    result = await session.call_tool("list_models", {})
                    models = json.loads(result.content[0].text)
                    if "available_models" in models and len(models["available_models"]) > 0:
                        print(f"✅ Models available: {models['available_models']}")
                        tests_passed += 1
                    else:
                        print(f"❌ No models found: {models}")
                except Exception as e:
                    print(f"❌ Model listing failed: {e}")
                
                # Test 4: Text Generation
                print("\n✍️  Test 4: Text Generation")
                tests_total += 1
                try:
                    result = await session.call_tool("generate", {
                        "prompt": "Write a haiku about AI",
                        "max_tokens": 100,
                        "temperature": 0.7
                    })
                    response = result.content[0].text
                    if len(response) > 10:  # Basic sanity check
                        print(f"✅ Generated text: {response[:100]}...")
                        tests_passed += 1
                    else:
                        print(f"❌ Generated text too short: {response}")
                except Exception as e:
                    print(f"❌ Text generation failed: {e}")
                
                # Test 5: Chat
                print("\n💬 Test 5: Chat Completion")
                tests_total += 1
                try:
                    result = await session.call_tool("chat", {
                        "messages": [
                            {"role": "user", "content": "Hello, how are you?"}
                        ],
                        "max_tokens": 50
                    })
                    response = result.content[0].text
                    if len(response) > 5:
                        print(f"✅ Chat response: {response[:100]}...")
                        tests_passed += 1
                    else:
                        print(f"❌ Chat response too short: {response}")
                except Exception as e:
                    print(f"❌ Chat failed: {e}")
                
                # Test 6: Classification
                print("\n🏷️  Test 6: Text Classification")
                tests_total += 1
                try:
                    result = await session.call_tool("classify", {
                        "text": "This product is amazing! I love it!",
                        "categories": ["positive", "negative", "neutral"]
                    })
                    classification = result.content[0].text.strip().lower()
                    if any(cat in classification for cat in ["positive", "negative", "neutral"]):
                        print(f"✅ Classification: {classification}")
                        tests_passed += 1
                    else:
                        print(f"❌ Invalid classification: {classification}")
                except Exception as e:
                    print(f"❌ Classification failed: {e}")
                
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
    
    # Results
    print(f"\n🎯 Test Results")
    print("=" * 20)
    print(f"Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! Phase 3 MCP server is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return tests_passed == tests_total

if __name__ == "__main__":
    success = asyncio.run(test_all_tools())
    exit(0 if success else 1)
