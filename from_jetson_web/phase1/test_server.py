#!/usr/bin/env python3
import requests
import json
import time
import asyncio

async def test_server():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Enhanced AI Server")
    print("=" * 40)
    
    # Test health
    print("1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   ✅ Health: {response.json()['status']}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test status
    print("2. System Status...")
    try:
        response = requests.get(f"{base_url}/status")
        status = response.json()
        print(f"   ✅ Active models: {len(status['active_models'])}")
        print(f"   ✅ Memory usage: {status['memory_usage_gb']:.1f}GB")
    except Exception as e:
        print(f"   ❌ Status check failed: {e}")
    
    # Test inference
    print("3. Single Inference...")
    try:
        test_request = {
            "prompt": "What is artificial intelligence?",
            "max_length": 30
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/inference", json=test_request)
        inference_time = time.time() - start_time
        
        result = response.json()
        print(f"   ✅ Response: {result['response'][:50]}...")
        print(f"   ✅ Model: {result['model_used']}")
        print(f"   ✅ Speed: {result['tokens_per_second']:.1f} tok/s")
        print(f"   ✅ Total time: {inference_time:.2f}s")
        
    except Exception as e:
        print(f"   ❌ Inference test failed: {e}")
    
    # Test batch inference
    print("4. Batch Inference...")
    try:
        batch_request = {
            "prompts": [
                "Hello, how are you?",
                "What is 2+2?",
                "Tell me a joke"
            ]
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/batch_inference", json=batch_request)
        batch_time = time.time() - start_time
        
        result = response.json()
        print(f"   ✅ Batch size: {result['batch_size']}")
        print(f"   ✅ Total time: {batch_time:.2f}s")
        print(f"   ✅ Avg per request: {result['avg_time_per_request']:.2f}s")
        
    except Exception as e:
        print(f"   ❌ Batch test failed: {e}")
    
    # Test performance endpoint
    print("5. Performance Analytics...")
    try:
        response = requests.get(f"{base_url}/performance")
        perf = response.json()
        
        if perf['system_report']['total_models_tested'] > 0:
            best_model = perf['system_report']['best_performing_model']
            print(f"   ✅ Best model: {best_model[0] if best_model else 'None'}")
        
        recent = perf['recent_performance']
        if recent:
            print(f"   ✅ Avg RAM: {recent.get('avg_ram_percent', 0):.1f}%")
            print(f"   ✅ Avg CPU: {recent.get('avg_cpu_percent', 0):.1f}%")
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_server())
