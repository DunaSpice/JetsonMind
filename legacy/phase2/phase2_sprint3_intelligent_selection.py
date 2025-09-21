#!/usr/bin/env python3
"""
Phase 2 Sprint 3: Intelligent Model Selection
Based on Sprint 2 findings: 4 RAM models (≤3GB), 2 swap models (≤7GB), reject >10.5GB
"""

import psutil
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ModelTier(Enum):
    RAM = "ram"      # ≤3GB, <0.3s load time
    SWAP = "swap"    # ≤7GB, ~3s load time  
    STORAGE = "storage"  # >7GB, rejected for safety

@dataclass
class ModelSpec:
    name: str
    size_gb: float
    tier: ModelTier
    load_time_estimate: float
    capabilities: List[str]

class IntelligentModelSelector:
    def __init__(self):
        # Model library based on Sprint 2 testing results
        self.model_library = {
            "gpt2-small": ModelSpec("gpt2-small", 0.5, ModelTier.RAM, 0.05, ["text-generation", "fast"]),
            "gpt2-medium": ModelSpec("gpt2-medium", 1.5, ModelTier.RAM, 0.15, ["text-generation", "balanced"]),
            "gpt2-large": ModelSpec("gpt2-large", 3.0, ModelTier.RAM, 0.30, ["text-generation", "quality"]),
            "bert-large": ModelSpec("bert-large", 1.3, ModelTier.RAM, 0.13, ["text-classification", "embeddings"]),
            "gpt-j-6b": ModelSpec("gpt-j-6b", 6.0, ModelTier.SWAP, 3.0, ["text-generation", "high-quality"]),
            "llama-7b": ModelSpec("llama-7b", 7.0, ModelTier.SWAP, 3.5, ["text-generation", "instruction-following"]),
            # Rejected models (too large)
            "llama-13b": ModelSpec("llama-13b", 13.0, ModelTier.STORAGE, float('inf'), ["text-generation", "premium"]),
            "codegen-16b": ModelSpec("codegen-16b", 16.0, ModelTier.STORAGE, float('inf'), ["code-generation", "premium"]),
        }
        
        self.current_model = None
        self.performance_preferences = {
            "speed": 1.0,      # Prefer faster models
            "quality": 0.7,    # Balance quality vs speed
            "capability": 0.8  # Match task requirements
        }
    
    def get_system_capacity(self) -> Dict:
        """Get current system capacity for model selection"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        ram_available_gb = memory.available / (1024**3)
        total_available_gb = (memory.available + swap.total - swap.used) / (1024**3)
        
        return {
            "ram_available_gb": ram_available_gb,
            "total_available_gb": total_available_gb,
            "can_load_ram": ram_available_gb > 1.0,  # 1GB safety margin
            "can_load_swap": total_available_gb > 3.0  # 3GB safety margin
        }
    
    def filter_available_models(self) -> List[ModelSpec]:
        """Filter models based on current system capacity"""
        capacity = self.get_system_capacity()
        available = []
        
        for model in self.model_library.values():
            if model.tier == ModelTier.RAM and capacity["can_load_ram"]:
                if model.size_gb <= capacity["ram_available_gb"] * 0.7:
                    available.append(model)
            elif model.tier == ModelTier.SWAP and capacity["can_load_swap"]:
                if model.size_gb <= capacity["total_available_gb"] * 0.6:
                    available.append(model)
            # STORAGE tier models are rejected
        
        return available
    
    def score_model(self, model: ModelSpec, task_requirements: List[str], 
                   performance_priority: str = "balanced") -> float:
        """Score model based on requirements and performance priority"""
        score = 0.0
        
        # Capability matching
        capability_match = len(set(model.capabilities) & set(task_requirements))
        score += capability_match * self.performance_preferences["capability"]
        
        # Performance scoring based on priority
        if performance_priority == "speed":
            # Prefer RAM models, penalize swap models
            if model.tier == ModelTier.RAM:
                score += 2.0
            elif model.tier == ModelTier.SWAP:
                score += 0.5
        elif performance_priority == "quality":
            # Prefer larger models regardless of tier
            score += model.size_gb * 0.2
        else:  # balanced
            # Balance between speed and quality
            if model.tier == ModelTier.RAM:
                score += 1.5
            elif model.tier == ModelTier.SWAP:
                score += 1.0 + (model.size_gb * 0.1)
        
        return score
    
    def select_optimal_model(self, task_requirements: List[str], 
                           performance_priority: str = "balanced",
                           explicit_model: Optional[str] = None) -> Tuple[Optional[ModelSpec], str]:
        """Select optimal model based on requirements and system capacity"""
        
        # Handle explicit model request
        if explicit_model:
            if explicit_model in self.model_library:
                model = self.model_library[explicit_model]
                available = self.filter_available_models()
                if model in available:
                    return model, f"Explicit model '{explicit_model}' selected"
                else:
                    return None, f"Model '{explicit_model}' unavailable (tier: {model.tier.value}, size: {model.size_gb}GB)"
            else:
                return None, f"Model '{explicit_model}' not found in library"
        
        # Intelligent selection
        available_models = self.filter_available_models()
        if not available_models:
            return None, "No models available for current system capacity"
        
        # Score and rank models
        scored_models = []
        for model in available_models:
            score = self.score_model(model, task_requirements, performance_priority)
            scored_models.append((model, score))
        
        # Select best model
        best_model, best_score = max(scored_models, key=lambda x: x[1])
        
        reason = f"Selected {best_model.name} (score: {best_score:.1f}, tier: {best_model.tier.value})"
        return best_model, reason

class Phase2Sprint3Server:
    def __init__(self):
        self.selector = IntelligentModelSelector()
    
    def handle_model_request(self, request: Dict) -> Dict:
        """Handle intelligent model selection request"""
        # Extract request parameters
        explicit_model = request.get("model")
        task_requirements = request.get("capabilities", ["text-generation"])
        performance_priority = request.get("priority", "balanced")
        
        # Select optimal model
        selected_model, reason = self.selector.select_optimal_model(
            task_requirements, performance_priority, explicit_model
        )
        
        if not selected_model:
            return {
                "status": "error",
                "reason": reason,
                "available_models": [m.name for m in self.selector.filter_available_models()]
            }
        
        # Simulate model loading
        load_time = selected_model.load_time_estimate
        
        return {
            "status": "success",
            "model": selected_model.name,
            "size_gb": selected_model.size_gb,
            "tier": selected_model.tier.value,
            "load_time": load_time,
            "capabilities": selected_model.capabilities,
            "selection_reason": reason
        }

def validate_sprint3():
    """Validate Sprint 3 intelligent selection"""
    server = Phase2Sprint3Server()
    
    print("🧠 Phase 2 Sprint 3: Intelligent Model Selection")
    print("=" * 50)
    
    test_cases = [
        {"test": "Speed Priority", "request": {"capabilities": ["text-generation"], "priority": "speed"}},
        {"test": "Quality Priority", "request": {"capabilities": ["text-generation"], "priority": "quality"}},
        {"test": "Explicit Model (RAM)", "request": {"model": "gpt2-large"}},
        {"test": "Explicit Model (Swap)", "request": {"model": "gpt-j-6b"}},
        {"test": "Explicit Model (Too Large)", "request": {"model": "llama-13b"}},
        {"test": "Classification Task", "request": {"capabilities": ["text-classification"]}},
        {"test": "Code Generation", "request": {"capabilities": ["code-generation"]}},
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\n🔍 {test_case['test']}")
        result = server.handle_model_request(test_case['request'])
        results.append(result)
        
        if result['status'] == 'success':
            print(f"  ✅ Selected: {result['model']} ({result['size_gb']}GB, {result['tier']})")
            print(f"  Load time: {result['load_time']:.2f}s")
            print(f"  Reason: {result['selection_reason']}")
        else:
            print(f"  ❌ Error: {result['reason']}")
            if 'available_models' in result:
                print(f"  Available: {', '.join(result['available_models'])}")
    
    # Summary
    successful = [r for r in results if r['status'] == 'success']
    print(f"\n📊 Sprint 3 Results:")
    print(f"  Test cases: {len(test_cases)}")
    print(f"  Successful selections: {len(successful)}")
    print(f"  Intelligence system: Active")
    
    return len(successful) >= 5  # Expect most tests to succeed

if __name__ == "__main__":
    validate_sprint3()
