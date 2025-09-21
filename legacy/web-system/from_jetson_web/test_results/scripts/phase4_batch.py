#!/usr/bin/env python3
import json
import time
from universal_test import test_model

# Phase 4: Medium LLM Models (1.7B-3B)
models_phase4 = [
    "HuggingFaceTB/SmolLM2-1.7B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "google/gemma-2-2b-it"
]

def run_phase4():
    results = []
    phase_name = "phase4_medium"
    
    print("🚀 Starting Phase 4: Medium LLM Models")
    print(f"Testing {len(models_phase4)} models...")
    
    for i, model in enumerate(models_phase4, 1):
        print(f"\n--- Model {i}/{len(models_phase4)} ---")
        
        result = test_model(model, phase_name)
        results.append(result)
        
        # Save after each test
        output_file = f"/results/phase4_medium/results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Cool down between tests
        if i < len(models_phase4):
            print("⏳ Cooling down 15 seconds...")
            time.sleep(15)
    
    print(f"\n✅ Phase 4 Complete! Results saved to {output_file}")
    return results

if __name__ == "__main__":
    run_phase4()
