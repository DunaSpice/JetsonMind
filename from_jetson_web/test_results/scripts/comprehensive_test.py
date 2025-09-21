#!/usr/bin/env python3
import torch
import time
import json
import psutil
import gc
import os
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM

class ComprehensiveMonitor:
    def __init__(self):
        self.start_time = time.time()
        
    def get_cpu_temp(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return int(f.read().strip()) / 1000
        except:
            return 0
    
    def get_nvme_stats(self):
        try:
            with open('/proc/diskstats', 'r') as f:
                for line in f:
                    if 'nvme0n1' in line:
                        parts = line.split()
                        return {
                            'reads': int(parts[3]),
                            'writes': int(parts[7]),
                            'read_sectors': int(parts[5]),
                            'write_sectors': int(parts[9])
                        }
        except:
            return {'reads': 0, 'writes': 0, 'read_sectors': 0, 'write_sectors': 0}
    
    def capture_full_metrics(self):
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - self.start_time,
            
            # Memory metrics
            'ram_total_gb': memory.total / 1024**3,
            'ram_used_gb': memory.used / 1024**3,
            'ram_available_gb': memory.available / 1024**3,
            'ram_percent': memory.percent,
            'swap_total_gb': swap.total / 1024**3,
            'swap_used_gb': swap.used / 1024**3,
            'swap_percent': swap.percent,
            
            # GPU metrics
            'gpu_memory_allocated_gb': torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0,
            'gpu_memory_reserved_gb': torch.cuda.memory_reserved() / 1024**3 if torch.cuda.is_available() else 0,
            
            # CPU metrics
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'cpu_temp_c': self.get_cpu_temp(),
            'load_avg_1m': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0,
            'cpu_count': psutil.cpu_count(),
            
            # Storage metrics
            'nvme_stats': self.get_nvme_stats(),
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'disk_free_gb': psutil.disk_usage('/').free / 1024**3,
        }

def comprehensive_model_test(model_name, model_size_b, test_prompts=None):
    if test_prompts is None:
        test_prompts = [
            "What is artificial intelligence?",
            "Explain quantum computing simply",
            "Write a Python function to sort a list"
        ]
    
    monitor = ComprehensiveMonitor()
    results = {
        'model_name': model_name,
        'model_size_b': model_size_b,
        'test_start': datetime.now().isoformat(),
        'phases': {}
    }
    
    print(f"🔬 COMPREHENSIVE TEST: {model_name} ({model_size_b}B)")
    
    # Phase 1: Baseline metrics
    print("📊 Phase 1: Baseline metrics")
    baseline = monitor.capture_full_metrics()
    results['phases']['baseline'] = baseline
    print(f"   RAM: {baseline['ram_used_gb']:.2f}GB/{baseline['ram_total_gb']:.2f}GB ({baseline['ram_percent']:.1f}%)")
    print(f"   Swap: {baseline['swap_used_gb']:.2f}GB/{baseline['swap_total_gb']:.2f}GB")
    print(f"   CPU: {baseline['cpu_percent']:.1f}% | Temp: {baseline['cpu_temp_c']:.1f}°C")
    
    # Phase 2: Model loading with monitoring
    print("📥 Phase 2: Model loading")
    load_start = time.time()
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="cuda"
        )
        
        load_time = time.time() - load_start
        post_load = monitor.capture_full_metrics()
        
        memory_delta = post_load['ram_used_gb'] - baseline['ram_used_gb']
        gpu_memory = post_load['gpu_memory_allocated_gb']
        
        results['phases']['post_load'] = post_load
        results['load_time'] = load_time
        results['memory_delta_gb'] = memory_delta
        results['gpu_memory_gb'] = gpu_memory
        
        print(f"   ✅ Loaded in {load_time:.1f}s")
        print(f"   Memory delta: +{memory_delta:.2f}GB")
        print(f"   GPU memory: {gpu_memory:.2f}GB")
        print(f"   RAM usage: {post_load['ram_percent']:.1f}%")
        
    except Exception as e:
        results['load_error'] = str(e)
        print(f"   ❌ Load failed: {e}")
        return results
    
    # Phase 3: Inference benchmarking
    print("🧠 Phase 3: Inference benchmarking")
    inference_results = []
    
    for i, prompt in enumerate(test_prompts):
        print(f"   Test {i+1}: {prompt[:30]}...")
        
        inference_start = time.time()
        pre_inference = monitor.capture_full_metrics()
        
        try:
            inputs = tokenizer.encode(prompt, return_tensors="pt").to("cuda")
            
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
            post_inference = monitor.capture_full_metrics()
            
            # Calculate tokens per second
            output_tokens = len(outputs[0]) - len(inputs[0])
            tokens_per_second = output_tokens / inference_time if inference_time > 0 else 0
            
            inference_result = {
                'prompt': prompt,
                'response': result,
                'inference_time': inference_time,
                'tokens_generated': output_tokens,
                'tokens_per_second': tokens_per_second,
                'pre_metrics': pre_inference,
                'post_metrics': post_inference
            }
            
            inference_results.append(inference_result)
            print(f"      ✅ {inference_time:.2f}s | {tokens_per_second:.1f} tok/s")
            
        except Exception as e:
            inference_results.append({
                'prompt': prompt,
                'error': str(e),
                'inference_time': time.time() - inference_start
            })
            print(f"      ❌ Failed: {e}")
    
    results['phases']['inference'] = inference_results
    
    # Phase 4: Memory pressure test
    print("💾 Phase 4: Memory pressure test")
    try:
        # Try to allocate additional memory to test limits
        pressure_start = time.time()
        test_tensors = []
        
        for i in range(5):
            tensor = torch.randn(100, 100, 100, dtype=torch.float16, device='cuda')
            test_tensors.append(tensor)
            current_metrics = monitor.capture_full_metrics()
            print(f"   Pressure test {i+1}: RAM {current_metrics['ram_percent']:.1f}%")
            
            if current_metrics['ram_percent'] > 95:
                print("   ⚠️ High memory pressure detected")
                break
        
        # Cleanup pressure test
        del test_tensors
        torch.cuda.empty_cache()
        
        pressure_time = time.time() - pressure_start
        results['phases']['pressure_test'] = {
            'duration': pressure_time,
            'max_pressure_reached': True
        }
        
    except Exception as e:
        results['phases']['pressure_test'] = {'error': str(e)}
        print(f"   ❌ Pressure test failed: {e}")
    
    # Phase 5: Cleanup and final metrics
    print("🧹 Phase 5: Cleanup")
    cleanup_start = time.time()
    
    del model, tokenizer
    torch.cuda.empty_cache()
    gc.collect()
    time.sleep(2)  # Let system settle
    
    cleanup_time = time.time() - cleanup_start
    final_metrics = monitor.capture_full_metrics()
    
    memory_recovered = post_load['ram_used_gb'] - final_metrics['ram_used_gb']
    
    results['phases']['final'] = final_metrics
    results['cleanup_time'] = cleanup_time
    results['memory_recovered_gb'] = memory_recovered
    results['test_duration'] = time.time() - monitor.start_time
    
    print(f"   ✅ Cleanup: {cleanup_time:.1f}s")
    print(f"   Memory recovered: {memory_recovered:.2f}GB")
    print(f"   Final RAM usage: {final_metrics['ram_percent']:.1f}%")
    
    # Summary
    print(f"\n📊 TEST SUMMARY:")
    print(f"   Model: {model_name} ({model_size_b}B)")
    print(f"   Load time: {results.get('load_time', 0):.1f}s")
    print(f"   Memory usage: {results.get('memory_delta_gb', 0):.2f}GB")
    print(f"   GPU memory: {results.get('gpu_memory_gb', 0):.2f}GB")
    if inference_results:
        avg_speed = sum(r.get('tokens_per_second', 0) for r in inference_results) / len(inference_results)
        print(f"   Avg inference: {avg_speed:.1f} tok/s")
    print(f"   Total test time: {results['test_duration']:.1f}s")
    
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 comprehensive_test.py <model_name> <model_size_b>")
        sys.exit(1)
    
    model_name = sys.argv[1]
    model_size_b = float(sys.argv[2])
    
    result = comprehensive_model_test(model_name, model_size_b)
    
    # Save detailed results
    output_file = f"/tmp/comprehensive_test_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
