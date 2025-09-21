#!/usr/bin/env python3
import json
import time
import subprocess
import sys

def run_phase(phase_script, phase_name):
    print(f"\n{'='*50}")
    print(f"🚀 STARTING {phase_name.upper()}")
    print(f"{'='*50}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            "python3", f"/results/scripts/{phase_script}"
        ], capture_output=True, text=True, timeout=3600)  # 1 hour timeout
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {phase_name} COMPLETED in {duration:.1f}s")
            return True
        else:
            print(f"❌ {phase_name} FAILED")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {phase_name} TIMEOUT after 1 hour")
        return False
    except Exception as e:
        print(f"❌ {phase_name} ERROR: {e}")
        return False

def main():
    phases = [
        ("phase3_batch.py", "Phase 3: Small Models (0.5B-1B)"),
        ("phase4_batch.py", "Phase 4: Medium Models (1.7B-3B)"),
        ("phase5_batch.py", "Phase 5: Large Models (7B-8B)")
    ]
    
    print("🎯 JETSON ORIN NANO - COMPREHENSIVE MODEL TESTING")
    print(f"Total phases to run: {len(phases)}")
    
    results_summary = []
    
    for phase_script, phase_name in phases:
        success = run_phase(phase_script, phase_name)
        results_summary.append({
            "phase": phase_name,
            "success": success,
            "timestamp": time.time()
        })
        
        if not success:
            print(f"\n⚠️  {phase_name} failed. Continue? (y/n): ", end="")
            if input().lower() != 'y':
                break
        
        # Break between phases
        print("\n⏳ 30 second break between phases...")
        time.sleep(30)
    
    # Final summary
    print(f"\n{'='*50}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*50}")
    
    for result in results_summary:
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"{result['phase']}: {status}")
    
    # Save summary
    with open("/results/execution_summary.json", "w") as f:
        json.dump(results_summary, f, indent=2)
    
    print("\n🎉 All phases completed!")

if __name__ == "__main__":
    main()
