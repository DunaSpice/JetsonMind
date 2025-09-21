#!/usr/bin/env python3
import json
import time
from universal_test import test_model

# Phase 3: Small LLM Models (0.5B-1B)
models_phase3 = [
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct", 
    "meta-llama/Llama-3.2-1B-Instruct"
]

def run_phase3():
    results = []
    phase_name = "phase3_small"
    
    print("🚀 Starting Phase 3: Small LLM Models")
    print(f"Testing {len(models_phase3)} models...")
    
    for i, model in enumerate(models_phase3, 1):
        print(f"\n--- Model {i}/{len(models_phase3)} ---")
        
        result = test_model(model, phase_name)
        results.append(result)
        
        # Save after each test
        output_file = f"/results/phase3_small/results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Cool down between tests
        if i < len(models_phase3):
            print("⏳ Cooling down 10 seconds...")
            time.sleep(10)
    
    print(f"\n✅ Phase 3 Complete! Results saved to {output_file}")
    return results

if __name__ == "__main__":
    run_phase3()
