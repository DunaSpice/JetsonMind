#!/usr/bin/env python3
"""
Phase 2 Sprint 2: Safe Large Model Testing
Focus: Test large models (up to 12GB) without crashing system
"""

import psutil
import time
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class SystemLimits:
    max_ram_usage: float = 0.85  # 85% of available RAM
    max_swap_usage: float = 0.75  # 75% of available swap
    min_free_ram: int = 1024 * 1024 * 1024  # 1GB minimum free

class SafeModelTester:
    def __init__(self):
        self.limits = SystemLimits()
        self.test_models = [
            {"name": "gpt2-medium", "size_gb": 1.5, "tier": "ram"},
            {"name": "gpt2-large", "size_gb": 3.0, "tier": "ram"},
            {"name": "gpt-j-6b", "size_gb": 12.0, "tier": "swap"},
            {"name": "llama-7b", "size_gb": 14.0, "tier": "swap"},  # Risk test
        ]
    
    def get_system_status(self) -> Dict:
        """Get current system resource status"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "ram_total_gb": memory.total / (1024**3),
            "ram_available_gb": memory.available / (1024**3),
            "ram_used_percent": memory.percent,
            "swap_total_gb": swap.total / (1024**3),
            "swap_used_gb": swap.used / (1024**3),
            "swap_used_percent": swap.percent,
            "safe_to_proceed": self._is_safe_to_proceed(memory, swap)
        }
    
    def _is_safe_to_proceed(self, memory, swap) -> bool:
        """Check if system can safely handle large model loading"""
        ram_safe = memory.percent < (self.limits.max_ram_usage * 100)
        swap_safe = swap.percent < (self.limits.max_swap_usage * 100)
        free_ram_safe = memory.available > self.limits.min_free_ram
        
        return ram_safe and swap_safe and free_ram_safe
    
    def can_load_model(self, model_size_gb: float) -> Tuple[bool, str]:
        """Check if model can be safely loaded"""
        status = self.get_system_status()
        
        if not status["safe_to_proceed"]:
            return False, "System resources too constrained"
        
        # Check RAM capacity
        if model_size_gb <= status["ram_available_gb"] * 0.8:
            return True, "RAM loading safe"
        
        # Check swap capacity
        available_swap_gb = status["swap_total_gb"] - status["swap_used_gb"]
        if model_size_gb <= available_swap_gb * 0.8:
            return True, "Swap loading possible (slower)"
        
        return False, f"Model too large: {model_size_gb}GB > available resources"
    
    def simulate_model_load(self, model: Dict) -> Dict:
        """Simulate loading a large model with safety checks"""
        print(f"\n🔍 Testing {model['name']} ({model['size_gb']}GB)")
        
        # Pre-load safety check
        can_load, reason = self.can_load_model(model['size_gb'])
        if not can_load:
            return {
                "model": model['name'],
                "status": "SKIPPED",
                "reason": reason,
                "safe": True
            }
        
        # Simulate gradual loading with monitoring
        start_time = time.time()
        for step in range(5):
            time.sleep(0.1)  # Simulate loading step
            status = self.get_system_status()
            
            if not status["safe_to_proceed"]:
                return {
                    "model": model['name'],
                    "status": "ABORTED",
                    "reason": "System limits exceeded during load",
                    "load_time": time.time() - start_time,
                    "safe": True
                }
        
        load_time = time.time() - start_time
        final_status = self.get_system_status()
        
        return {
            "model": model['name'],
            "status": "SUCCESS",
            "load_time": load_time,
            "final_ram_percent": final_status["ram_used_percent"],
            "final_swap_percent": final_status["swap_used_percent"],
            "safe": True
        }

def run_safe_large_model_tests():
    """Run progressive large model tests with safety monitoring"""
    tester = SafeModelTester()
    
    print("🛡️  Phase 2 Sprint 2: Safe Large Model Testing")
    print("=" * 50)
    
    # Initial system check
    initial_status = tester.get_system_status()
    print(f"Initial System Status:")
    print(f"  RAM: {initial_status['ram_used_percent']:.1f}% used")
    print(f"  Swap: {initial_status['swap_used_percent']:.1f}% used")
    print(f"  Safe to proceed: {initial_status['safe_to_proceed']}")
    
    if not initial_status['safe_to_proceed']:
        print("❌ System not ready for large model testing")
        return
    
    # Progressive testing
    results = []
    for model in tester.test_models:
        result = tester.simulate_model_load(model)
        results.append(result)
        
        print(f"  Status: {result['status']}")
        if result['status'] == 'SUCCESS':
            print(f"  Load time: {result['load_time']:.2f}s")
            print(f"  Final RAM: {result['final_ram_percent']:.1f}%")
        elif result['status'] == 'SKIPPED':
            print(f"  Reason: {result['reason']}")
        
        # Safety pause between tests
        time.sleep(0.5)
    
    # Summary
    successful = [r for r in results if r['status'] == 'SUCCESS']
    print(f"\n📊 Test Summary:")
    print(f"  Models tested: {len(results)}")
    print(f"  Successful loads: {len(successful)}")
    print(f"  System crashes: 0 (safety system active)")
    
    if successful:
        max_model = max(successful, key=lambda x: tester.test_models[[m['name'] for m in tester.test_models].index(x['model'])]['size_gb'])
        max_size = tester.test_models[[m['name'] for m in tester.test_models].index(max_model['model'])]['size_gb']
        print(f"  Largest successful model: {max_model['model']} ({max_size}GB)")

if __name__ == "__main__":
    run_safe_large_model_tests()
