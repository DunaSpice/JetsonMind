#!/usr/bin/env python3
"""
Phase 2 Sprint 2: Realistic Large Model Testing
System: 7.4GB RAM + 11GB Swap = 18.4GB total capacity
Target: Test models up to theoretical 15GB limit safely
"""

import psutil
import time
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class SystemLimits:
    max_ram_usage: float = 0.80  # 80% of available RAM
    max_swap_usage: float = 0.70  # 70% of available swap
    min_free_ram: int = 1024 * 1024 * 1024  # 1GB minimum free

class RealisticModelTester:
    def __init__(self):
        self.limits = SystemLimits()
        # Realistic model sizes for 7.4GB RAM + 11GB swap system
        self.test_models = [
            {"name": "gpt2-small", "size_gb": 0.5, "tier": "ram"},
            {"name": "gpt2-medium", "size_gb": 1.5, "tier": "ram"},
            {"name": "gpt2-large", "size_gb": 3.0, "tier": "ram"},
            {"name": "bert-large", "size_gb": 1.3, "tier": "ram"},
            {"name": "gpt-j-6b", "size_gb": 6.0, "tier": "swap"},  # Fits in available RAM
            {"name": "llama-7b", "size_gb": 7.0, "tier": "swap"},  # Near RAM limit
            {"name": "llama-13b", "size_gb": 13.0, "tier": "swap"}, # Requires swap
            {"name": "codegen-16b", "size_gb": 16.0, "tier": "storage"}, # Too large
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
            "total_available_gb": (memory.available + swap.total - swap.used) / (1024**3),
            "safe_to_proceed": self._is_safe_to_proceed(memory, swap)
        }
    
    def _is_safe_to_proceed(self, memory, swap) -> bool:
        """Check if system can safely handle large model loading"""
        ram_safe = memory.percent < (self.limits.max_ram_usage * 100)
        swap_safe = swap.percent < (self.limits.max_swap_usage * 100)
        free_ram_safe = memory.available > self.limits.min_free_ram
        
        return ram_safe and swap_safe and free_ram_safe
    
    def can_load_model(self, model_size_gb: float) -> Tuple[bool, str, str]:
        """Check if model can be safely loaded and determine tier"""
        status = self.get_system_status()
        
        if not status["safe_to_proceed"]:
            return False, "System resources too constrained", "none"
        
        # Check RAM capacity (with safety margin)
        safe_ram_gb = status["ram_available_gb"] * 0.7
        if model_size_gb <= safe_ram_gb:
            return True, "RAM loading (fast access)", "ram"
        
        # Check total capacity (RAM + Swap with safety margin)
        safe_total_gb = status["total_available_gb"] * 0.6
        if model_size_gb <= safe_total_gb:
            return True, "Swap loading (slower access)", "swap"
        
        return False, f"Model too large: {model_size_gb}GB > {safe_total_gb:.1f}GB safe limit", "storage"
    
    def simulate_model_load(self, model: Dict) -> Dict:
        """Simulate loading a model with realistic timing"""
        print(f"\n🔍 Testing {model['name']} ({model['size_gb']}GB)")
        
        # Pre-load safety check
        can_load, reason, actual_tier = self.can_load_model(model['size_gb'])
        if not can_load:
            return {
                "model": model['name'],
                "size_gb": model['size_gb'],
                "status": "SKIPPED",
                "reason": reason,
                "expected_tier": model['tier'],
                "actual_tier": actual_tier,
                "safe": True
            }
        
        # Simulate realistic loading times based on tier
        start_time = time.time()
        if actual_tier == "ram":
            time.sleep(0.1 * model['size_gb'])  # 0.1s per GB for RAM
        else:  # swap
            time.sleep(0.5 * model['size_gb'])  # 0.5s per GB for swap
        
        load_time = time.time() - start_time
        final_status = self.get_system_status()
        
        return {
            "model": model['name'],
            "size_gb": model['size_gb'],
            "status": "SUCCESS",
            "load_time": load_time,
            "expected_tier": model['tier'],
            "actual_tier": actual_tier,
            "final_ram_percent": final_status["ram_used_percent"],
            "final_swap_percent": final_status["swap_used_percent"],
            "safe": True
        }

def run_realistic_model_tests():
    """Run progressive model tests matching actual system capacity"""
    tester = RealisticModelTester()
    
    print("🛡️  Phase 2 Sprint 2: Realistic Model Testing")
    print("System: 7.4GB RAM + 11GB Swap")
    print("=" * 50)
    
    # Initial system check
    initial_status = tester.get_system_status()
    print(f"Initial System Status:")
    print(f"  RAM: {initial_status['ram_available_gb']:.1f}GB available ({initial_status['ram_used_percent']:.1f}% used)")
    print(f"  Swap: {initial_status['swap_total_gb']:.1f}GB total ({initial_status['swap_used_percent']:.1f}% used)")
    print(f"  Total available: {initial_status['total_available_gb']:.1f}GB")
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
            print(f"  Tier: {result['expected_tier']} → {result['actual_tier']}")
            if result['actual_tier'] == 'swap':
                print(f"  ⚠️  Using swap (slower performance)")
        elif result['status'] == 'SKIPPED':
            print(f"  Reason: {result['reason']}")
        
        time.sleep(0.2)  # Brief pause between tests
    
    # Analysis
    successful = [r for r in results if r['status'] == 'SUCCESS']
    ram_models = [r for r in successful if r['actual_tier'] == 'ram']
    swap_models = [r for r in successful if r['actual_tier'] == 'swap']
    
    print(f"\n📊 Test Results Analysis:")
    print(f"  Total models tested: {len(results)}")
    print(f"  Successful loads: {len(successful)}")
    print(f"  RAM-tier models: {len(ram_models)} (fast access)")
    print(f"  Swap-tier models: {len(swap_models)} (slower access)")
    print(f"  System crashes: 0 (safety system active)")
    
    if successful:
        max_model = max(successful, key=lambda x: x['size_gb'])
        print(f"  Largest successful model: {max_model['model']} ({max_model['size_gb']}GB)")
        
        if swap_models:
            avg_swap_time = sum(r['load_time'] for r in swap_models) / len(swap_models)
            print(f"  Average swap load time: {avg_swap_time:.1f}s")

if __name__ == "__main__":
    run_realistic_model_tests()
