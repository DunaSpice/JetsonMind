#!/usr/bin/env python3
"""
Automated MCP Client Assignment Runner
Executes all assignment tasks and provides scoring
"""

import asyncio
import json
import subprocess
import time
from typing import Dict, List, Tuple

class MCPAssignmentRunner:
    def __init__(self):
        self.score = 0
        self.max_score = 25
        self.results = []
        
    async def run_mcp_tool(self, tool_name: str, arguments: dict, timeout: int = 10) -> dict:
        """Run a single MCP tool and return result"""
        try:
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "assignment", "version": "1.0"}},
                "id": 1
            }
            
            tool_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
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
                timeout=timeout
            )
            
            if process.returncode == 0:
                lines = stdout.decode().strip().split('\n')
                if len(lines) >= 2:
                    return json.loads(lines[1])
            
            return {"error": f"Process failed: {stderr.decode()}"}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def task_1_system_status(self) -> Tuple[int, str]:
        """Task 1: System Status Check (2 points)"""
        result = await self.run_mcp_tool("get_system_status", {})
        
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"][0]["text"]
            if "operational" in content.lower():
                return 2, "✅ System status operational"
            else:
                return 1, "⚠️ System responding but status unclear"
        
        return 0, "❌ System status check failed"
    
    async def task_2_model_discovery(self) -> Tuple[int, str]:
        """Task 2: Model Discovery (2 points)"""
        result = await self.run_mcp_tool("list_models", {})
        
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"][0]["text"]
            expected_models = ["gpt2-small", "gpt2-medium", "gpt2-large", "bert-large", "gpt-j-6b", "llama-7b"]
            found_models = sum(1 for model in expected_models if model in content)
            
            if found_models >= 6:
                return 2, f"✅ All {found_models} models discovered"
            elif found_models >= 4:
                return 1, f"⚠️ {found_models}/6 models found"
            else:
                return 0, f"❌ Only {found_models}/6 models found"
        
        return 0, "❌ Model discovery failed"
    
    async def task_3_memory_analysis(self) -> Tuple[int, str]:
        """Task 3: Memory Analysis (2 points)"""
        result = await self.run_mcp_tool("get_memory_status", {})
        
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"][0]["text"]
            if "ram_total_gb" in content and "jetsonmind" in content:
                return 2, "✅ Memory analysis complete"
            else:
                return 1, "⚠️ Partial memory data"
        
        return 0, "❌ Memory analysis failed"
    
    async def task_4_model_info(self) -> Tuple[int, str]:
        """Task 4: Model Information (2 points)"""
        result = await self.run_mcp_tool("get_model_info", {"model_name": "llama-7b"})
        
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"][0]["text"]
            if "7.0" in content and "swap" in content and "thinking_capable" in content:
                return 2, "✅ Model info detailed and accurate"
            else:
                return 1, "⚠️ Model info partial"
        
        return 0, "❌ Model info failed"
    
    async def task_5_smart_selection(self) -> Tuple[int, str]:
        """Task 5: Smart Model Selection (3 points)"""
        # Test 1: Code generation
        result1 = await self.run_mcp_tool("select_optimal_model", {"prompt": "Write Python code for data analysis"})
        
        # Test 2: Long text
        long_prompt = " ".join(["word"] * 150)
        result2 = await self.run_mcp_tool("select_optimal_model", {"prompt": long_prompt})
        
        score = 0
        details = []
        
        if "result" in result1 and "codellama" in str(result1).lower():
            score += 1.5
            details.append("✅ Code detection works")
        else:
            details.append("❌ Code detection failed")
        
        if "result" in result2 and "llama-13b" in str(result2):
            score += 1.5
            details.append("✅ Long text detection works")
        else:
            details.append("❌ Long text detection failed")
        
        return int(score), f"Smart selection: {'; '.join(details)}"
    
    async def task_6_text_generation(self) -> Tuple[int, str]:
        """Task 6: Text Generation (3 points)"""
        result1 = await self.run_mcp_tool("generate_text", {"prompt": "Hello AI", "thinking_mode": "immediate"})
        result2 = await self.run_mcp_tool("generate_text", {"prompt": "Plan a project", "thinking_mode": "strategic"})
        
        score = 0
        if "result" in result1:
            score += 1.5
        if "result" in result2:
            score += 1.5
        
        return int(score), f"✅ Text generation: {score}/3 modes working"
    
    async def task_7_model_management(self) -> Tuple[int, str]:
        """Task 7: Model Management (2 points)"""
        load_result = await self.run_mcp_tool("manage_model_loading", {"action": "load", "model_name": "gpt2-small"})
        unload_result = await self.run_mcp_tool("manage_model_loading", {"action": "unload", "model_name": "gpt2-small"})
        
        score = 0
        if "result" in load_result:
            score += 1
        if "result" in unload_result:
            score += 1
        
        return score, f"✅ Model management: {score}/2 operations working"
    
    async def task_8_hot_swapping(self) -> Tuple[int, str]:
        """Task 8: Hot Model Swapping (2 points)"""
        result = await self.run_mcp_tool("hot_swap_models", {"source_model": "gpt2-small", "target_model": "gpt2-medium"})
        
        if "result" in result:
            return 2, "✅ Hot swapping operational"
        
        return 0, "❌ Hot swapping failed"
    
    async def task_9_batch_processing(self) -> Tuple[int, str]:
        """Task 9: Batch Processing (3 points)"""
        prompts = ["Hello world", "Generate code", "Analyze data", "Write documentation"]
        result = await self.run_mcp_tool("batch_inference", {"prompts": prompts}, timeout=15)
        
        if "result" in result and "content" in result["result"]:
            content = result["result"]["content"][0]["text"]
            response_count = content.count("1.") + content.count("2.") + content.count("3.") + content.count("4.")
            
            if response_count >= 4:
                return 3, "✅ Batch processing: All 4 responses generated"
            elif response_count >= 2:
                return 2, f"⚠️ Batch processing: {response_count}/4 responses"
            else:
                return 1, "⚠️ Batch processing: Partial success"
        
        return 0, "❌ Batch processing failed"
    
    async def task_10_agent_sessions(self) -> Tuple[int, str]:
        """Task 10: Agent Session Management (2 points)"""
        result = await self.run_mcp_tool("create_agent_session", {"session_id": "coding-assistant"})
        
        if "result" in result:
            return 2, "✅ Agent session created"
        
        return 0, "❌ Agent session failed"
    
    def task_11_q_cli_integration(self) -> Tuple[int, str]:
        """Task 11: Q CLI Integration Test (3 points)"""
        try:
            # Check MCP configuration
            result = subprocess.run(["q", "mcp", "list"], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stderr
                if "jetsonmind-enhanced" in output and "hf-spaces" in output:
                    return 3, "✅ Q CLI: Both MCP servers configured"
                elif "jetsonmind-enhanced" in output:
                    return 2, "⚠️ Q CLI: JetsonMind MCP configured"
                else:
                    return 1, "⚠️ Q CLI: Partial configuration"
            
            return 0, "❌ Q CLI: Configuration check failed"
            
        except Exception as e:
            return 0, f"❌ Q CLI: {str(e)[:50]}"
    
    async def run_all_tasks(self):
        """Run all assignment tasks"""
        print("🚀 Running MCP Client Assignment")
        print("=" * 50)
        
        tasks = [
            ("Task 1: System Status", self.task_1_system_status),
            ("Task 2: Model Discovery", self.task_2_model_discovery),
            ("Task 3: Memory Analysis", self.task_3_memory_analysis),
            ("Task 4: Model Information", self.task_4_model_info),
            ("Task 5: Smart Selection", self.task_5_smart_selection),
            ("Task 6: Text Generation", self.task_6_text_generation),
            ("Task 7: Model Management", self.task_7_model_management),
            ("Task 8: Hot Swapping", self.task_8_hot_swapping),
            ("Task 9: Batch Processing", self.task_9_batch_processing),
            ("Task 10: Agent Sessions", self.task_10_agent_sessions),
        ]
        
        # Run async tasks
        for task_name, task_func in tasks:
            print(f"\n🔄 {task_name}...")
            try:
                points, message = await task_func()
                self.score += points
                self.results.append(f"{task_name}: {message} ({points} pts)")
                print(f"   {message} ({points} pts)")
            except Exception as e:
                self.results.append(f"{task_name}: ❌ Error: {str(e)[:50]} (0 pts)")
                print(f"   ❌ Error: {str(e)[:50]} (0 pts)")
        
        # Run sync task
        print(f"\n🔄 Task 11: Q CLI Integration...")
        try:
            points, message = self.task_11_q_cli_integration()
            self.score += points
            self.results.append(f"Task 11: Q CLI Integration: {message} ({points} pts)")
            print(f"   {message} ({points} pts)")
        except Exception as e:
            self.results.append(f"Task 11: Q CLI Integration: ❌ Error: {str(e)[:50]} (0 pts)")
            print(f"   ❌ Error: {str(e)[:50]} (0 pts)")
    
    def print_summary(self):
        """Print final assignment summary"""
        print("\n" + "=" * 50)
        print("📊 ASSIGNMENT RESULTS SUMMARY")
        print("=" * 50)
        
        for result in self.results:
            print(f"  {result}")
        
        percentage = (self.score / self.max_score) * 100
        
        print(f"\n🎯 FINAL SCORE: {self.score}/{self.max_score} ({percentage:.1f}%)")
        
        if percentage >= 92:
            grade = "✅ EXCELLENT - Production Ready!"
        elif percentage >= 72:
            grade = "✅ GOOD - Core functionality working"
        elif percentage >= 52:
            grade = "⚠️ NEEDS WORK - Major components working"
        else:
            grade = "❌ FAILED - System requires debugging"
        
        print(f"📋 GRADE: {grade}")
        
        return self.score, self.max_score, percentage

async def main():
    runner = MCPAssignmentRunner()
    
    start_time = time.time()
    await runner.run_all_tasks()
    elapsed = time.time() - start_time
    
    score, max_score, percentage = runner.print_summary()
    
    print(f"\n⏱️ Assignment completed in {elapsed:.1f} seconds")
    print(f"🎯 System Status: {'OPERATIONAL' if percentage >= 80 else 'NEEDS ATTENTION'}")

if __name__ == "__main__":
    asyncio.run(main())
