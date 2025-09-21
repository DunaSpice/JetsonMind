#!/usr/bin/env python3
import json
import time
from universal_test import test_model

# Phase 5: Large LLM Models (7B-8B)
models_phase5 = [
    "Qwen/Qwen2.5-7B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct"
]

def run_phase5():
    results = []
    phase_name = "phase5_large"
    
    print("🚀 Starting Phase 5: Large LLM Models")
    print(f"Testing {len(models_phase5)} models...")
    print("⚠️  WARNING: These models may require significant memory!")
    
    for i, model in enumerate(models_phase5, 1):
        print(f"\n--- Model {i}/{len(models_phase5)} ---")
        
        result = test_model(model, phase_name)
        results.append(result)
        
        # Save after each test
        output_file = f"/results/phase5_large/results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Cool down between tests
        if i < len(models_phase5):
            print("⏳ Cooling down 20 seconds...")
            time.sleep(20)
    
    print(f"\n✅ Phase 5 Complete! Results saved to {output_file}")
    return results

if __name__ == "__main__":
    run_phase5()
