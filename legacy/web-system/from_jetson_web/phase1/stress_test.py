#!/usr/bin/env python3
import asyncio
import aiohttp
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics

class StressTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        
    async def test_concurrent_load(self):
        """Test concurrent request handling"""
        print("🔥 CONCURRENT LOAD TEST")
        print("-" * 30)
        
        async with aiohttp.ClientSession() as session:
            # Test increasing concurrent loads
            for concurrency in [2, 5, 10, 15]:
                print(f"Testing {concurrency} concurrent requests...")
                
                tasks = []
                start_time = time.time()
                
                for i in range(concurrency):
                    task = self.make_inference_request(session, f"Test {i}")
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                duration = time.time() - start_time
                
                successful = sum(1 for r in results if isinstance(r, dict) and 'response' in r)
                throughput = successful / duration
                
                print(f"  ✅ {successful}/{concurrency} successful ({throughput:.1f} req/s)")
                
                self.results[f"concurrent_{concurrency}"] = {
                    "successful": successful,
                    "total": concurrency,
                    "duration": duration,
                    "throughput": throughput
                }
                
                await asyncio.sleep(2)  # Cool down
    
    async def test_memory_pressure(self):
        """Test system under memory pressure"""
        print("\n💾 MEMORY PRESSURE TEST")
        print("-" * 30)
        
        async with aiohttp.ClientSession() as session:
            # Load multiple models to create memory pressure
            models_to_load = ["microsoft/DialoGPT-small", "microsoft/DialoGPT-medium"]
            
            for model in models_to_load:
                print(f"Loading {model}...")
                try:
                    async with session.post(f"{self.base_url}/load_model", 
                                          json={"model_name": model}) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"  ✅ Loaded in {data.get('load_time', 0):.1f}s")
                        else:
                            print(f"  ❌ Failed to load {model}")
                except Exception as e:
                    print(f"  ❌ Error loading {model}: {e}")
                
                # Check memory status
                try:
                    async with session.get(f"{self.base_url}/status") as response:
                        if response.status == 200:
                            status = await response.json()
                            memory_gb = status.get("memory_usage_gb", 0)
                            memory_pct = (memory_gb / status.get("memory_budget_gb", 7.4)) * 100
                            print(f"  📊 Memory: {memory_gb:.1f}GB ({memory_pct:.1f}%)")
                except:
                    pass
    
    async def test_sustained_load(self):
        """Test sustained load over time"""
        print("\n⏱️ SUSTAINED LOAD TEST (60s)")
        print("-" * 30)
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            request_count = 0
            response_times = []
            
            while time.time() - start_time < 60:  # Run for 60 seconds
                try:
                    request_start = time.time()
                    result = await self.make_inference_request(session, "Sustained test")
                    request_time = time.time() - request_start
                    
                    if isinstance(result, dict) and 'response' in result:
                        request_count += 1
                        response_times.append(request_time)
                        
                        if request_count % 10 == 0:
                            avg_time = statistics.mean(response_times[-10:])
                            print(f"  📊 {request_count} requests, avg: {avg_time:.2f}s")
                    
                    await asyncio.sleep(0.5)  # 2 requests per second
                    
                except Exception as e:
                    print(f"  ❌ Request failed: {e}")
            
            duration = time.time() - start_time
            throughput = request_count / duration
            
            self.results["sustained_load"] = {
                "duration": duration,
                "total_requests": request_count,
                "throughput": throughput,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "p95_response_time": sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
            }
            
            print(f"  ✅ Completed: {request_count} requests in {duration:.1f}s ({throughput:.2f} req/s)")
    
    async def test_optimization_trigger(self):
        """Test automatic optimization"""
        print("\n🔧 OPTIMIZATION TEST")
        print("-" * 30)
        
        async with aiohttp.ClientSession() as session:
            # Get initial status
            async with session.get(f"{self.base_url}/status") as response:
                initial_status = await response.json()
                initial_memory = initial_status.get("memory_usage_gb", 0)
            
            print(f"Initial memory: {initial_memory:.1f}GB")
            
            # Trigger optimization
            async with session.post(f"{self.base_url}/optimize") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"  ✅ Optimization: {result.get('message', 'Unknown')}")
                else:
                    print("  ❌ Optimization failed")
            
            # Check final status
            await asyncio.sleep(2)
            async with session.get(f"{self.base_url}/status") as response:
                final_status = await response.json()
                final_memory = final_status.get("memory_usage_gb", 0)
            
            memory_change = final_memory - initial_memory
            print(f"Final memory: {final_memory:.1f}GB (change: {memory_change:+.1f}GB)")
    
    async def make_inference_request(self, session, prompt):
        """Make a single inference request"""
        try:
            async with session.post(f"{self.base_url}/inference",
                                  json={"prompt": prompt, "max_length": 15},
                                  timeout=30) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    def generate_report(self):
        """Generate stress test report"""
        print("\n📊 STRESS TEST REPORT")
        print("=" * 40)
        
        # Concurrent load results
        print("\n🔥 Concurrent Load Performance:")
        for test_name, result in self.results.items():
            if test_name.startswith("concurrent_"):
                concurrency = test_name.split("_")[1]
                success_rate = (result["successful"] / result["total"]) * 100
                print(f"  {concurrency} concurrent: {success_rate:.1f}% success, {result['throughput']:.1f} req/s")
        
        # Sustained load results
        if "sustained_load" in self.results:
            sustained = self.results["sustained_load"]
            print(f"\n⏱️ Sustained Load Performance:")
            print(f"  Total requests: {sustained['total_requests']}")
            print(f"  Throughput: {sustained['throughput']:.2f} req/s")
            print(f"  Avg response time: {sustained['avg_response_time']:.2f}s")
            print(f"  P95 response time: {sustained['p95_response_time']:.2f}s")
        
        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        
        # Check if system handles concurrent load well
        high_concurrency = [r for name, r in self.results.items() 
                           if name.startswith("concurrent_") and int(name.split("_")[1]) >= 10]
        
        if high_concurrency and high_concurrency[0]["successful"] / high_concurrency[0]["total"] > 0.8:
            print("  ✅ Excellent concurrent load handling")
        else:
            print("  ⚠️ Concurrent load performance needs optimization")
        
        # Check sustained performance
        if "sustained_load" in self.results and self.results["sustained_load"]["throughput"] > 1.0:
            print("  ✅ Good sustained performance")
        else:
            print("  ⚠️ Sustained performance below target")
        
        print(f"\n💾 Results saved to stress_test_results.json")
        with open("stress_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)

async def main():
    tester = StressTester()
    
    await tester.test_concurrent_load()
    await tester.test_memory_pressure()
    await tester.test_sustained_load()
    await tester.test_optimization_trigger()
    
    tester.generate_report()

if __name__ == "__main__":
    asyncio.run(main())
