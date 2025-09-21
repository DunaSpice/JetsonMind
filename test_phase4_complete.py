#!/usr/bin/env python3
"""
Phase 4 Complete System Test
Tests JetsonMind MCP → HuggingFace MCP → Real AI integration
"""

import asyncio
import json
import subprocess
import time

async def test_jetsonmind_mcp():
    """Test our 10 JetsonMind MCP tools"""
    print("🧠 Testing JetsonMind MCP System...")
    
    tools_to_test = [
        ("list_models", {}),
        ("generate_text", {"prompt": "Hello AI"}),
        ("get_system_status", {}),
        ("get_memory_status", {}),
        ("manage_model_loading", {"action": "load", "model_name": "gpt2-small"}),
        ("get_model_info", {"model_name": "gpt2-small"}),
        ("select_optimal_model", {"prompt": "Generate code"}),
        ("hot_swap_models", {"source_model": "gpt2-small", "target_model": "gpt2-medium"}),
        ("batch_inference", {"prompts": ["Hello", "World"]}),
        ("create_agent_session", {"session_id": "test-session"})
    ]
    
    results = []
    for tool_name, args in tools_to_test:
        try:
            # Test each tool
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}},
                "id": 1
            }
            
            tool_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": args},
                "id": 2
            }
            
            input_data = json.dumps(init_request) + "\n" + json.dumps(tool_request) + "\n"
            
            process = await asyncio.create_subprocess_exec(
                "/home/petr/jetson/core/run_mcp_server.sh",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input_data.encode()), 
                timeout=10
            )
            
            if process.returncode == 0:
                lines = stdout.decode().strip().split('\n')
                if len(lines) >= 2:
                    response = json.loads(lines[1])
                    if 'result' in response:
                        results.append(f"✅ {tool_name}: Working")
                    else:
                        results.append(f"❌ {tool_name}: No result")
                else:
                    results.append(f"❌ {tool_name}: Invalid response")
            else:
                results.append(f"❌ {tool_name}: Process failed")
                
        except asyncio.TimeoutError:
            results.append(f"⏰ {tool_name}: Timeout")
        except Exception as e:
            results.append(f"❌ {tool_name}: {str(e)[:50]}")
    
    return results

async def test_hf_mcp():
    """Test HuggingFace MCP integration"""
    print("🤗 Testing HuggingFace MCP Integration...")
    
    try:
        process = await asyncio.create_subprocess_exec(
            "npx", "@llmindset/mcp-hfspace",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}},
            "id": 1
        }
        
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        input_data = json.dumps(init_request) + "\n" + json.dumps(tools_request) + "\n"
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input_data.encode()),
            timeout=15
        )
        
        if process.returncode == 0:
            lines = stdout.decode().strip().split('\n')
            if len(lines) >= 2:
                response = json.loads(lines[1])
                if 'result' in response and 'tools' in response['result']:
                    tools = response['result']['tools']
                    return f"✅ HF MCP: {len(tools)} tools available"
        
        return "❌ HF MCP: Failed to get tools"
        
    except Exception as e:
        return f"❌ HF MCP: {str(e)[:50]}"

def test_q_cli_integration():
    """Test Q CLI MCP integration"""
    print("🎯 Testing Q CLI Integration...")
    
    try:
        result = subprocess.run(
            ["q", "mcp", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stderr  # Q CLI outputs to stderr
            if "jetsonmind-enhanced" in output and "hf-spaces" in output:
                return "✅ Q CLI: Both MCP servers configured"
            elif "jetsonmind-enhanced" in output:
                return "⚠️ Q CLI: JetsonMind MCP only"
            else:
                return "❌ Q CLI: No MCP servers found"
        else:
            return f"❌ Q CLI: Command failed ({result.returncode})"
            
    except Exception as e:
        return f"❌ Q CLI: {str(e)[:50]}"

async def main():
    """Run comprehensive Phase 4 system test"""
    print("🚀 Phase 4 Complete System Test")
    print("=" * 50)
    
    start_time = time.time()
    
    # Test 1: JetsonMind MCP System
    jetsonmind_results = await test_jetsonmind_mcp()
    
    # Test 2: HuggingFace MCP
    hf_result = await test_hf_mcp()
    
    # Test 3: Q CLI Integration
    q_cli_result = test_q_cli_integration()
    
    # Results Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    print("\n🧠 JetsonMind MCP Tools:")
    for result in jetsonmind_results:
        print(f"  {result}")
    
    print(f"\n🤗 HuggingFace MCP:")
    print(f"  {hf_result}")
    
    print(f"\n🎯 Q CLI Integration:")
    print(f"  {q_cli_result}")
    
    # Calculate success rate
    jetsonmind_success = len([r for r in jetsonmind_results if r.startswith("✅")])
    total_tests = len(jetsonmind_results) + 2  # +2 for HF and Q CLI
    
    success_rate = ((jetsonmind_success + 
                    (1 if hf_result.startswith("✅") else 0) + 
                    (1 if q_cli_result.startswith("✅") else 0)) / total_tests) * 100
    
    elapsed = time.time() - start_time
    
    print(f"\n🎯 Overall Results:")
    print(f"  Success Rate: {success_rate:.1f}% ({jetsonmind_success + (1 if hf_result.startswith('✅') else 0) + (1 if q_cli_result.startswith('✅') else 0)}/{total_tests})")
    print(f"  Test Duration: {elapsed:.1f}s")
    
    if success_rate >= 80:
        print(f"  Status: ✅ PHASE 4 SUCCESS - System Ready!")
    elif success_rate >= 60:
        print(f"  Status: ⚠️ PHASE 4 PARTIAL - Needs optimization")
    else:
        print(f"  Status: ❌ PHASE 4 FAILED - Requires fixes")

if __name__ == "__main__":
    asyncio.run(main())
