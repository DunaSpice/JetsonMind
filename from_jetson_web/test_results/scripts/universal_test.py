#!/usr/bin/env python3
import torch
import time
import json
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_model(model_name, phase, test_prompt="Hello, how are you?"):
    results = {
        "model": model_name,
        "phase": phase,
        "status": "unknown",
        "load_time": 0,
        "inference_time": 0,
        "output": "",
        "error": "",
        "gpu_memory_gb": 0
    }
    
    print(f"🔄 Testing {model_name}...")
    start_time = time.time()
    
    try:
        # Load model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="cuda"
        )
        
        load_time = time.time() - start_time
        
        # Check GPU memory
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated() / 1024**3
        else:
            gpu_memory = 0
        
        # Test inference
        inference_start = time.time()
        inputs = tokenizer.encode(test_prompt, return_tensors="pt").to("cuda")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + 10,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id
            )
        
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        inference_time = time.time() - inference_start
        
        results.update({
            "status": "success",
            "load_time": round(load_time, 2),
            "inference_time": round(inference_time, 2),
            "output": result,
            "gpu_memory_gb": round(gpu_memory, 2)
        })
        
        print(f"✅ SUCCESS: {model_name}")
        print(f"   Load time: {load_time:.2f}s")
        print(f"   GPU memory: {gpu_memory:.2f}GB")
        print(f"   Output: {result[:50]}...")
        
    except Exception as e:
        results.update({
            "status": "failed",
            "error": str(e)
        })
        print(f"❌ FAILED: {model_name} - {str(e)}")
    
    # Cleanup
    if 'model' in locals():
        del model
    if 'tokenizer' in locals():
        del tokenizer
    torch.cuda.empty_cache()
    
    return results

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 universal_test.py <model_name> <phase>")
        sys.exit(1)
    
    model_name = sys.argv[1]
    phase = sys.argv[2]
    
    result = test_model(model_name, phase)
    print(json.dumps(result, indent=2))
