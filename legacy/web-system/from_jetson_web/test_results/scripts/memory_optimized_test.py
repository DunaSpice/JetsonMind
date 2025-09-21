#!/usr/bin/env python3
import torch
import time
import json
import sys
import gc
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from system_monitor import start_monitoring, stop_monitoring, get_stats, check_safety

def force_cleanup():
    """Aggressive memory cleanup"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    time.sleep(2)  # Let system settle

def get_model_config(model_name, model_size_b):
    """Get optimized model configuration based on size"""
    config = {
        "torch_dtype": torch.float16,
        "device_map": "cuda",
        "low_cpu_mem_usage": True,  # Reduces peak memory during loading
    }
    
    # Use quantization for models >1.5B
    if model_size_b > 1.5:
        print(f"🔧 Using 4-bit quantization for {model_size_b}B model")
        config["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
    
    return config

def memory_optimized_test(model_name, phase, model_size_b, test_prompt="Hello, how are you?"):
    results = {
        "model": model_name,
        "phase": phase,
        "model_size_b": model_size_b,
        "status": "unknown",
        "load_time": 0,
        "inference_time": 0,
        "tokens_per_second": 0,
        "output": "",
        "error": "",
        "gpu_memory_gb": 0,
        "peak_memory_percent": 0,
        "memory_optimization": "none",
        "pre_test_stats": {},
        "post_test_stats": {}
    }
    
    print(f"🔄 Testing {model_name} ({model_size_b}B parameters)...")
    
    # Pre-test cleanup
    force_cleanup()
    
    # Start monitoring
    start_monitoring()
    time.sleep(2)
    
    # Pre-test stats
    results["pre_test_stats"] = get_stats()
    
    # Safety check
    safe, alerts = check_safety()
    if not safe:
        results.update({
            "status": "aborted_unsafe",
            "error": "System not safe for testing",
            "safety_alerts": alerts
        })
        stop_monitoring()
        return results
    
    start_time = time.time()
    
    try:
        print("📥 Loading model with memory optimizations...")
        
        # Get optimized config
        model_config = get_model_config(model_name, model_size_b)
        
        # Record optimization used
        if "quantization_config" in model_config:
            results["memory_optimization"] = "4bit_quantization"
        else:
            results["memory_optimization"] = "low_cpu_mem_usage"
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Safety check during loading
        safe, alerts = check_safety()
        if not safe:
            results.update({
                "status": "aborted_during_load",
                "error": "System became unsafe during loading",
                "safety_alerts": alerts
            })
            stop_monitoring()
            return results
        
        # Load model with optimizations
        model = AutoModelForCausalLM.from_pretrained(model_name, **model_config)
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f}s with {results['memory_optimization']}")
        
        # Check GPU memory
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated() / 1024**3
        else:
            gpu_memory = 0
        
        # Safety check after loading
        safe, alerts = check_safety()
        if not safe:
            results.update({
                "status": "aborted_after_load",
                "error": "System became unsafe after loading",
                "load_time": load_time,
                "gpu_memory_gb": gpu_memory
            })
            stop_monitoring()
            return results
        
        print("🧠 Running inference...")
        
        # Test inference
        inference_start = time.time()
        inputs = tokenizer.encode(test_prompt, return_tensors="pt").to("cuda")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + 20,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id
            )
        
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        inference_time = time.time() - inference_start
        
        # Calculate performance
        tokens_per_second = len(result.split()) / inference_time if inference_time > 0 else 0
        
        # Get peak memory from monitoring
        peak_memory = max([d.get('memory_percent', 0) for d in monitor.data[-10:]] or [0])
        
        results.update({
            "status": "success",
            "load_time": round(load_time, 2),
            "inference_time": round(inference_time, 2),
            "tokens_per_second": round(tokens_per_second, 2),
            "output": result,
            "gpu_memory_gb": round(gpu_memory, 2),
            "peak_memory_percent": round(peak_memory, 1)
        })
        
        print(f"✅ SUCCESS: {model_name}")
        print(f"   Optimization: {results['memory_optimization']}")
        print(f"   Load time: {load_time:.2f}s")
        print(f"   Speed: {tokens_per_second:.2f} tokens/sec")
        print(f"   GPU memory: {gpu_memory:.2f}GB")
        print(f"   Peak RAM: {peak_memory:.1f}%")
        
    except Exception as e:
        results.update({
            "status": "failed",
            "error": str(e)
        })
        print(f"❌ FAILED: {model_name} - {str(e)}")
    
    # Post-test stats
    results["post_test_stats"] = get_stats()
    
    # Aggressive cleanup
    if 'model' in locals():
        del model
    if 'tokenizer' in locals():
        del tokenizer
    
    force_cleanup()
    stop_monitoring()
    
    print("⏳ Extended cooling down 15 seconds...")
    time.sleep(15)
    
    return results

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 memory_optimized_test.py <model_name> <phase> <model_size_b>")
        sys.exit(1)
    
    model_name = sys.argv[1]
    phase = sys.argv[2]
    model_size_b = float(sys.argv[3])
    
    result = memory_optimized_test(model_name, phase, model_size_b)
    print(json.dumps(result, indent=2))
