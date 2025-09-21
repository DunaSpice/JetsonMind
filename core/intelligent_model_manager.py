#!/usr/bin/env python3
"""
Intelligent Model Manager - Phase 5
Capability-first, compatibility-focused, scalable architecture
"""

import asyncio
import psutil
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    TTS = "text-to-speech"
    STT = "speech-to-text" 
    CODING = "code-generation"
    REASONING = "logical-reasoning"
    OS_TASKS = "system-administration"
    MCP_TOOLS = "tool-calling"
    GENERAL = "general-intelligence"

@dataclass
class ModelCapability:
    model_name: str
    task_types: List[TaskType]
    memory_mb: int
    load_time_ms: int
    mcp_optimized: bool
    tool_calling_score: int  # 1-10

class IntelligentModelManager:
    """Capability-first model management with scalability"""
    
    def __init__(self):
        self.active_models = {}
        self.model_capabilities = self._init_model_capabilities()
        self.task_queue = asyncio.Queue()
        self.resource_monitor = ResourceMonitor()
        
    def _init_model_capabilities(self) -> Dict[str, ModelCapability]:
        """Initialize model capability database"""
        return {
            "phi-3-mini": ModelCapability(
                model_name="phi-3-mini",
                task_types=[TaskType.CODING, TaskType.REASONING, TaskType.MCP_TOOLS],
                memory_mb=2300,
                load_time_ms=800,
                mcp_optimized=True,
                tool_calling_score=9
            ),
            "whisper-small": ModelCapability(
                model_name="whisper-small", 
                task_types=[TaskType.STT],
                memory_mb=244,
                load_time_ms=200,
                mcp_optimized=False,
                tool_calling_score=3
            ),
            "codeqwen-1.5b": ModelCapability(
                model_name="codeqwen-1.5b",
                task_types=[TaskType.CODING, TaskType.OS_TASKS, TaskType.MCP_TOOLS],
                memory_mb=1800,
                load_time_ms=600,
                mcp_optimized=True,
                tool_calling_score=8
            ),
            "piper-tts": ModelCapability(
                model_name="piper-tts",
                task_types=[TaskType.TTS],
                memory_mb=50,
                load_time_ms=100,
                mcp_optimized=False,
                tool_calling_score=2
            ),
            "starcoder2-3b": ModelCapability(
                model_name="starcoder2-3b",
                task_types=[TaskType.CODING],
                memory_mb=3200,
                load_time_ms=1200,
                mcp_optimized=True,
                tool_calling_score=7
            )
        }
    
    async def select_optimal_model(self, task_type: TaskType, 
                                 priority_mcp: bool = True) -> str:
        """Intelligent model selection based on capability and resources"""
        
        # Filter models by capability
        capable_models = [
            name for name, cap in self.model_capabilities.items()
            if task_type in cap.task_types
        ]
        
        if not capable_models:
            return "phi-3-mini"  # Fallback to general model
        
        # Priority scoring
        def score_model(model_name: str) -> float:
            cap = self.model_capabilities[model_name]
            score = 0.0
            
            # MCP optimization bonus
            if priority_mcp and cap.mcp_optimized:
                score += 3.0
            
            # Tool calling capability
            score += cap.tool_calling_score * 0.3
            
            # Resource efficiency (lower memory = higher score)
            score += (5000 - cap.memory_mb) / 1000
            
            # Load time efficiency
            score += (2000 - cap.load_time_ms) / 500
            
            # Already loaded bonus
            if model_name in self.active_models:
                score += 2.0
                
            return score
        
        # Select highest scoring model
        best_model = max(capable_models, key=score_model)
        return best_model
    
    async def ensure_model_loaded(self, model_name: str) -> bool:
        """Ensure model is loaded with resource management"""
        if model_name in self.active_models:
            return True
            
        # Check resources
        cap = self.model_capabilities[model_name]
        if not self.resource_monitor.can_load_model(cap.memory_mb):
            # Free up space by unloading least important models
            await self._free_memory_for_model(cap.memory_mb)
        
        # Load model
        try:
            print(f"🔄 Loading {model_name} ({cap.memory_mb}MB)...")
            await asyncio.sleep(cap.load_time_ms / 1000)  # Simulate load time
            self.active_models[model_name] = {
                "loaded_at": asyncio.get_event_loop().time(),
                "usage_count": 0,
                "capability": cap
            }
            print(f"✅ {model_name} loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to load {model_name}: {e}")
            return False
    
    async def _free_memory_for_model(self, required_mb: int):
        """Intelligent model unloading to free memory"""
        available_mb = self.resource_monitor.get_available_memory_mb()
        
        if available_mb >= required_mb:
            return
            
        # Sort by importance (usage, recency, capability)
        models_by_importance = sorted(
            self.active_models.items(),
            key=lambda x: (
                x[1]["usage_count"],  # Less used first
                x[1]["loaded_at"],    # Older first
                -x[1]["capability"].tool_calling_score  # Lower capability first
            )
        )
        
        freed_mb = 0
        for model_name, info in models_by_importance:
            if freed_mb >= required_mb:
                break
                
            print(f"🗑️ Unloading {model_name} to free memory...")
            freed_mb += info["capability"].memory_mb
            del self.active_models[model_name]
    
    async def process_task(self, task_type: TaskType, content: str) -> str:
        """Process task with optimal model selection"""
        # Select optimal model
        model_name = await self.select_optimal_model(task_type, priority_mcp=True)
        
        # Ensure model is loaded
        if not await self.ensure_model_loaded(model_name):
            return f"❌ Failed to load model for {task_type.value}"
        
        # Update usage stats
        self.active_models[model_name]["usage_count"] += 1
        
        # Process with model (simulated)
        print(f"🧠 Processing {task_type.value} with {model_name}")
        await asyncio.sleep(0.1)  # Simulate processing
        
        return f"✅ {task_type.value} completed by {model_name}: {content[:50]}..."

class ResourceMonitor:
    """Monitor system resources for intelligent scheduling"""
    
    def get_available_memory_mb(self) -> int:
        """Get available system memory in MB"""
        return int(psutil.virtual_memory().available / (1024 * 1024))
    
    def get_gpu_utilization(self) -> float:
        """Get GPU utilization percentage"""
        # Placeholder - would use nvidia-ml-py in real implementation
        return 45.0
    
    def get_temperature(self) -> float:
        """Get system temperature"""
        # Placeholder - would read from thermal sensors
        return 65.0
    
    def can_load_model(self, required_mb: int) -> bool:
        """Check if model can be loaded given current resources"""
        available_mb = self.get_available_memory_mb()
        temperature = self.get_temperature()
        
        # Thermal throttling
        if temperature > 75:
            return required_mb < 1000  # Only small models when hot
        
        # Memory check with safety margin
        return available_mb > (required_mb + 1000)

# Example usage
async def demo_intelligent_manager():
    """Demonstrate intelligent model management"""
    manager = IntelligentModelManager()
    
    # Process different tasks
    tasks = [
        (TaskType.CODING, "Write a Python function to sort a list"),
        (TaskType.STT, "Convert speech to text"),
        (TaskType.MCP_TOOLS, "Call the file system tool"),
        (TaskType.TTS, "Convert text to speech"),
        (TaskType.OS_TASKS, "List directory contents")
    ]
    
    for task_type, content in tasks:
        result = await manager.process_task(task_type, content)
        print(f"Result: {result}\n")

if __name__ == "__main__":
    asyncio.run(demo_intelligent_manager())
