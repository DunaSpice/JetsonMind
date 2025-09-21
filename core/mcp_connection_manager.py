#!/usr/bin/env python3
"""
MCP Connection Manager - Handle connection issues and provide direct access
"""
import json
import subprocess
import asyncio
import sys
import os

class MCPConnectionManager:
    """Manage MCP connections and provide direct tool access"""
    
    def __init__(self, server_path="/home/petr/jetson/core/mcp_server_enhanced.py"):
        self.server_path = server_path
        self.server_dir = os.path.dirname(server_path)
    
    def call_tool_direct(self, tool_name: str, arguments: dict = None) -> dict:
        """Call MCP tool directly when connection is down"""
        if arguments is None:
            arguments = {}
            
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            # Call server directly
            process = subprocess.run(
                ["python3", self.server_path],
                input=json.dumps(request),
                capture_output=True,
                text=True,
                cwd=self.server_dir,
                timeout=30
            )
            
            if process.returncode == 0 and process.stdout:
                result = json.loads(process.stdout.strip())
                return result.get("result", {}).get("content", [{}])[0].get("text", "No response")
            else:
                return f"❌ Direct call failed: {process.stderr}"
                
        except Exception as e:
            return f"❌ Connection error: {str(e)}"
    
    def test_system_limits(self):
        """Test all system capabilities"""
        print("🚀 Testing Phase 5 System Limits via Direct MCP Connection")
        print("=" * 60)
        
        # Test 1: Maximum batch processing
        print("\n🔥 Test 1: Maximum Batch Processing")
        batch_result = self.call_tool_direct("batch_inference", {
            "prompts": [
                "Create FastAPI endpoint with JWT auth",
                "Write async PostgreSQL connection pool", 
                "Build WebSocket real-time handler",
                "Generate comprehensive error middleware",
                "Design microservices architecture",
                "Implement Redis caching system",
                "Create automated testing pipeline",
                "Build Docker multi-stage deployment",
                "Optimize Jetson CUDA utilization",
                "Design scalable API gateway"
            ]
        })
        print(batch_result)
        
        # Test 2: Intelligent model selection
        print("\n🎯 Test 2: Intelligent Model Selection")
        model_result = self.call_tool_direct("select_optimal_model", {
            "prompt": "Real-time speech-to-text on Jetson Orin with CUDA, <100ms latency, 95% accuracy, noisy environment"
        })
        print(model_result)
        
        # Test 3: Memory limits
        print("\n💾 Test 3: Memory Status and Limits")
        memory_result = self.call_tool_direct("get_memory_status")
        print(memory_result)
        
        # Test 4: System status
        print("\n🚀 Test 4: System Status")
        status_result = self.call_tool_direct("get_system_status")
        print(status_result)
        
        # Test 5: Model management
        print("\n🤖 Test 5: Model Management")
        models_result = self.call_tool_direct("list_models")
        print(models_result)
        
        # Test 6: Hot swap capabilities
        print("\n🔄 Test 6: Hot Swap Test")
        swap_result = self.call_tool_direct("hot_swap_models", {
            "source_model": "llama-7b",
            "target_model": "codellama-7b"
        })
        print(swap_result)
        
        print("\n✅ Phase 5 System Limits Test Complete!")

if __name__ == "__main__":
    manager = MCPConnectionManager()
    manager.test_system_limits()
