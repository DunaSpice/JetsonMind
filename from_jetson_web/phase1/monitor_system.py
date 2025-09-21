#!/usr/bin/env python3
import requests
import time
import json

def monitor_server():
    base_url = "http://localhost:8000"
    
    while True:
        try:
            # Get status
            status = requests.get(f"{base_url}/status").json()
            
            print(f"\n📊 System Status - {time.strftime('%H:%M:%S')}")
            print(f"  Active Models: {len(status['active_models'])}")
            print(f"  Memory: {status['memory_usage_gb']:.1f}GB / {status['memory_budget_gb']:.1f}GB")
            print(f"  CPU: {status['cpu_percent']:.1f}%")
            print(f"  GPU Memory: {status['gpu_memory_gb']:.1f}GB")
            print(f"  Temperature: {status['temperature_c']:.1f}°C")
            print(f"  Queue Size: {status['queue_size']}")
            
            if status['alerts']:
                print(f"  🚨 Alerts: {len(status['alerts'])}")
                for alert in status['alerts'][-3:]:
                    print(f"    - {alert['type']}: {alert['message']}")
            
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
        
        time.sleep(10)

if __name__ == "__main__":
    monitor_server()
