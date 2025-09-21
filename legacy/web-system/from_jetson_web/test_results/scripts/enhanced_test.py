#!/usr/bin/env python3
import torch
import time
import json
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM
from system_monitor import monitor, start_monitoring, stop_monitoring, get_stats, check_safety

def calculate_tokens_per_second(text, inference_time):
    """Calculate approximate tokens per second"""
    # Rough estimate: ~4 characters per token
    estimated_tokens = len(text) / 4
    return estimated_tokens / inference_time if inference_time > 0 else 0

def test_model_enhanced(model_name, phase, test_prompt="Hello, how are you?"):
    results = {
        "model": model_name,
        "phase": phase,
        "status": "unknown",
        "load_time": 0,
        "inference_time": 0,
        "tokens_per_second": 0,
        "output": "",
        "error": "",
        "gpu_memory_gb": 0,
        "peak_gpu_temp": 0,
        "peak_memory_percent": 0,
        "safety_alerts": [],
        "pre_test_stats": {},
        "post_test_stats": {}
    }
    
    print(f"🔄 Testing {model_name}...")
    
    # Start monitoring
    start_monitoring()
    time.sleep(2)  # Let monitoring stabilize
    
    # Pre-test stats
    results["pre_test_stats"] = get_stats()
    
    # Safety check before starting
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
        print("📥 Loading model...")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Safety check during loading
        safe, alerts = check_safety()
        if not safe:
            results.update({
                "status": "aborted_during_load",
                "error": "System became unsafe during model loading",
                "safety_alerts": alerts
            })
            stop_monitoring()
            return results
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="cuda"
        )
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f}s")
        
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
                "error": "System became unsafe after model loading",
                "safety_alerts": alerts,
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
                max_length=inputs.shape[1] + 20,  # Generate more tokens for better speed measurement
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id
            )
        
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        inference_time = time.time() - inference_start
        
        # Calculate performance metrics
        tokens_per_second = calculate_tokens_per_second(result, inference_time)
        
        # Get peak stats from monitoring
        peak_gpu_temp = max([d.get('gpu_temp_c', 0) for d in monitor.data[-10:]] or [0])
        peak_memory = max([d.get('memory_percent', 0) for d in monitor.data[-10:]] or [0])
        
        results.update({
            "status": "success",
            "load_time": round(load_time, 2),
            "inference_time": round(inference_time, 2),
            "tokens_per_second": round(tokens_per_second, 2),
            "output": result,
            "gpu_memory_gb": round(gpu_memory, 2),
            "peak_gpu_temp": peak_gpu_temp,
            "peak_memory_percent": round(peak_memory, 1),
            "safety_alerts": monitor.alerts[-5:] if monitor.alerts else []  # Last 5 alerts
        })
        
        print(f"✅ SUCCESS: {model_name}")
        print(f"   Load time: {load_time:.2f}s")
        print(f"   Inference time: {inference_time:.2f}s")
        print(f"   Speed: {tokens_per_second:.2f} tokens/sec")
        print(f"   GPU memory: {gpu_memory:.2f}GB")
        print(f"   Peak GPU temp: {peak_gpu_temp}°C")
        print(f"   Output: {result[:80]}...")
        
    except Exception as e:
        results.update({
            "status": "failed",
            "error": str(e),
            "safety_alerts": monitor.alerts[-5:] if monitor.alerts else []
        })
        print(f"❌ FAILED: {model_name} - {str(e)}")
    
    # Post-test stats
    results["post_test_stats"] = get_stats()
    
    # Cleanup
    if 'model' in locals():
        del model
    if 'tokenizer' in locals():
        del tokenizer
    torch.cuda.empty_cache()
    
    # Stop monitoring
    stop_monitoring()
    
    # Cool down period
    print("⏳ Cooling down 10 seconds...")
    time.sleep(10)
    
    return results

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 enhanced_test.py <model_name> <phase>")
        sys.exit(1)
    
    model_name = sys.argv[1]
    phase = sys.argv[2]
    
    result = test_model_enhanced(model_name, phase)
    print(json.dumps(result, indent=2))
