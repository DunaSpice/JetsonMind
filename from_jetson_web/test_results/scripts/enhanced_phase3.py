#!/usr/bin/env python3
import json
import time
import os
from datetime import datetime
from enhanced_test import test_model_enhanced
from system_monitor import start_monitoring, stop_monitoring, save_data, get_stats

# Phase 3: Small LLM Models (0.5B-1B)
models_phase3 = [
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct", 
    "meta-llama/Llama-3.2-1B-Instruct"
]

def print_progress_bar(current, total, model_name=""):
    """Print a progress bar"""
    percent = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\r🔄 Progress: [{bar}] {percent:.1f}% - {model_name}", end='', flush=True)

def print_system_status():
    """Print current system status"""
    stats = get_stats()
    print(f"\n📊 System Status:")
    print(f"   CPU: {stats['cpu_percent']:.1f}% | Temp: {stats['cpu_temp_c']:.1f}°C")
    print(f"   Memory: {stats['memory_percent']:.1f}% ({stats['memory_available_gb']:.1f}GB free)")
    print(f"   GPU: {stats['gpu_utilization_percent']}% | Temp: {stats['gpu_temp_c']}°C")
    print(f"   GPU Memory: {stats['gpu_memory_used_mb']:.0f}MB / {stats['gpu_memory_total_mb']:.0f}MB")

def run_enhanced_phase3():
    results = []
    phase_name = "phase3_small"
    
    print("🚀 ENHANCED PHASE 3: Small LLM Models with Comprehensive Monitoring")
    print(f"Testing {len(models_phase3)} models with safety monitoring...")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initial system check
    print_system_status()
    
    # Create results directory
    os.makedirs("/results/phase3_small", exist_ok=True)
    
    total_start_time = time.time()
    
    for i, model in enumerate(models_phase3, 1):
        print(f"\n{'='*60}")
        print(f"🎯 Model {i}/{len(models_phase3)}: {model}")
        print(f"{'='*60}")
        
        # Update progress
        print_progress_bar(i-1, len(models_phase3), model.split('/')[-1])
        
        # Pre-model system status
        print_system_status()
        
        # Run test with enhanced monitoring
        result = test_model_enhanced(model, phase_name)
        results.append(result)
        
        # Save results after each test
        output_file = "/results/phase3_small/results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save monitoring data
        monitoring_file = f"/results/phase3_small/monitoring_{i}.json"
        save_data(monitoring_file)
        
        # Print test summary
        if result["status"] == "success":
            print(f"✅ {model.split('/')[-1]}: {result['tokens_per_second']:.1f} tok/s, {result['gpu_memory_gb']:.1f}GB")
        else:
            print(f"❌ {model.split('/')[-1]}: {result['status']} - {result['error'][:50]}...")
        
        # Safety check between models
        if result.get("safety_alerts"):
            print("⚠️ Safety alerts detected:")
            for alert in result["safety_alerts"]:
                print(f"   {alert}")
        
        # Extended cool down between tests
        if i < len(models_phase3):
            print(f"\n⏳ Cooling down 30 seconds before next model...")
            for countdown in range(30, 0, -5):
                print(f"   Next test in {countdown}s...", end='\r')
                time.sleep(5)
            print("   Ready for next test!     ")
    
    # Final progress
    print_progress_bar(len(models_phase3), len(models_phase3), "COMPLETE")
    
    total_time = time.time() - total_start_time
    
    # Final summary
    print(f"\n\n{'='*60}")
    print("📊 PHASE 3 FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Models tested: {len(results)}")
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] != "success"]
    
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        print(f"\n🏆 Performance Summary:")
        for result in successful:
            model_name = result["model"].split('/')[-1]
            print(f"   {model_name}: {result['tokens_per_second']:.1f} tok/s, {result['gpu_memory_gb']:.1f}GB")
    
    if failed:
        print(f"\n💥 Failures:")
        for result in failed:
            model_name = result["model"].split('/')[-1]
            print(f"   {model_name}: {result['status']}")
    
    # Save final summary
    summary = {
        "phase": phase_name,
        "total_time_minutes": round(total_time/60, 1),
        "models_tested": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "completion_time": datetime.now().isoformat(),
        "results": results
    }
    
    with open("/results/phase3_small/summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Phase 3 Complete! Results saved to {output_file}")
    print(f"📊 Summary saved to /results/phase3_small/summary.json")
    
    return results

if __name__ == "__main__":
    run_enhanced_phase3()
