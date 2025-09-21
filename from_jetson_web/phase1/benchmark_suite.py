#!/usr/bin/env python3
import asyncio
import aiohttp
import time
import json
import statistics
import psutil
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import numpy as np

class PerformanceBenchmark:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        
    async def run_benchmarks(self):
        """Run comprehensive performance benchmarks"""
        print("⚡ PERFORMANCE BENCHMARK SUITE")
        print("=" * 50)
        
        # Benchmark 1: Throughput Test
        await self.benchmark_throughput()
        
        # Benchmark 2: Latency Distribution
        await self.benchmark_latency()
        
        # Benchmark 3: Concurrent Load
        await self.benchmark_concurrent_load()
        
        # Benchmark 4: Memory Efficiency
        await self.benchmark_memory_efficiency()
        
        # Benchmark 5: Model Swap Performance
        await self.benchmark_model_swapping()
        
        # Generate performance report
        self.generate_performance_report()
        
    async def benchmark_throughput(self):
        """Measure requests per second"""
        print("\n🚀 Throughput Benchmark")
        
        async with aiohttp.ClientSession() as session:
            test_request = {"prompt": "Throughput test", "max_length": 10}
            
            # Warm up
            for _ in range(3):
                await self.make_request(session, "/inference", test_request)
            
            # Measure throughput over 60 seconds
            start_time = time.time()
            successful_requests = 0
            response_times = []
            
            while time.time() - start_time < 60:
                request_start = time.time()
                success = await self.make_request(session, "/inference", test_request)
                request_time = time.time() - request_start
                
                if success:
                    successful_requests += 1
                    response_times.append(request_time)
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
            
            duration = time.time() - start_time
            throughput = successful_requests / duration
            
            self.results["throughput"] = {
                "requests_per_second": throughput,
                "total_requests": successful_requests,
                "duration": duration,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "p95_response_time": np.percentile(response_times, 95) if response_times else 0
            }
            
            print(f"  📊 Throughput: {throughput:.2f} req/s")
            print(f"  📊 Total requests: {successful_requests}")
            print(f"  📊 Avg response time: {statistics.mean(response_times):.2f}s")
    
    async def benchmark_latency(self):
        """Measure latency distribution"""
        print("\n⏱️ Latency Benchmark")
        
        async with aiohttp.ClientSession() as session:
            latencies = []
            test_request = {"prompt": "Latency test", "max_length": 15}
            
            # Collect 100 samples
            for i in range(100):
                start_time = time.time()
                success = await self.make_request(session, "/inference", test_request)
                latency = time.time() - start_time
                
                if success:
                    latencies.append(latency)
                
                if i % 20 == 0:
                    print(f"  Progress: {i}/100 samples")
                
                await asyncio.sleep(0.5)  # Space out requests
            
            if latencies:
                self.results["latency"] = {
                    "min": min(latencies),
                    "max": max(latencies),
                    "mean": statistics.mean(latencies),
                    "median": statistics.median(latencies),
                    "p90": np.percentile(latencies, 90),
                    "p95": np.percentile(latencies, 95),
                    "p99": np.percentile(latencies, 99),
                    "std_dev": statistics.stdev(latencies)
                }
                
                print(f"  📊 Mean latency: {statistics.mean(latencies):.2f}s")
                print(f"  📊 P95 latency: {np.percentile(latencies, 95):.2f}s")
                print(f"  📊 P99 latency: {np.percentile(latencies, 99):.2f}s")
    
    async def benchmark_concurrent_load(self):
        """Test concurrent request handling"""
        print("\n🔄 Concurrent Load Benchmark")
        
        async def concurrent_test(concurrency_level):
            async with aiohttp.ClientSession() as session:
                test_request = {"prompt": f"Concurrent test", "max_length": 10}
                
                tasks = []
                start_time = time.time()
                
                for _ in range(concurrency_level):
                    task = self.make_request(session, "/inference", test_request)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                duration = time.time() - start_time
                
                successful = sum(1 for r in results if r is True)
                return successful, duration, concurrency_level
        
        # Test different concurrency levels
        concurrency_levels = [1, 2, 4, 8, 12]
        concurrent_results = []
        
        for level in concurrency_levels:
            print(f"  Testing concurrency level: {level}")
            successful, duration, level = await concurrent_test(level)
            throughput = successful / duration
            
            concurrent_results.append({
                "concurrency": level,
                "successful_requests": successful,
                "duration": duration,
                "throughput": throughput,
                "success_rate": successful / level
            })
            
            print(f"    Success rate: {successful}/{level} ({successful/level*100:.1f}%)")
            print(f"    Throughput: {throughput:.2f} req/s")
        
        self.results["concurrent_load"] = concurrent_results
    
    async def benchmark_memory_efficiency(self):
        """Measure memory usage patterns"""
        print("\n💾 Memory Efficiency Benchmark")
        
        async with aiohttp.ClientSession() as session:
            # Get initial memory state
            initial_status = await self.get_status(session)
            initial_memory = initial_status.get("memory_usage_gb", 0)
            
            memory_samples = []
            
            # Run inference while monitoring memory
            for i in range(20):
                test_request = {"prompt": f"Memory test {i}", "max_length": 20}
                await self.make_request(session, "/inference", test_request)
                
                status = await self.get_status(session)
                if status:
                    memory_samples.append(status.get("memory_usage_gb", 0))
                
                await asyncio.sleep(1)
            
            if memory_samples:
                self.results["memory_efficiency"] = {
                    "initial_memory_gb": initial_memory,
                    "min_memory_gb": min(memory_samples),
                    "max_memory_gb": max(memory_samples),
                    "avg_memory_gb": statistics.mean(memory_samples),
                    "memory_variance": statistics.variance(memory_samples),
                    "memory_growth": max(memory_samples) - initial_memory
                }
                
                print(f"  📊 Initial memory: {initial_memory:.2f}GB")
                print(f"  📊 Peak memory: {max(memory_samples):.2f}GB")
                print(f"  📊 Memory growth: {max(memory_samples) - initial_memory:.2f}GB")
    
    async def benchmark_model_swapping(self):
        """Benchmark model loading and swapping performance"""
        print("\n🔄 Model Swapping Benchmark")
        
        async with aiohttp.ClientSession() as session:
            models_to_test = [
                "Qwen/Qwen2.5-0.5B-Instruct",
                "Qwen/Qwen2.5-1.5B-Instruct"
            ]
            
            swap_results = []
            
            for model in models_to_test:
                print(f"  Testing model: {model}")
                
                # Load model and measure time
                load_request = {"model_name": model, "priority": "normal"}
                start_time = time.time()
                
                success = await self.make_request(session, "/load_model", load_request)
                load_time = time.time() - start_time
                
                if success:
                    # Test inference speed
                    inference_request = {"prompt": "Test inference", "max_length": 15}
                    inference_start = time.time()
                    await self.make_request(session, "/inference", inference_request)
                    inference_time = time.time() - inference_start
                    
                    swap_results.append({
                        "model": model,
                        "load_time": load_time,
                        "inference_time": inference_time,
                        "success": True
                    })
                    
                    print(f"    Load time: {load_time:.2f}s")
                    print(f"    Inference time: {inference_time:.2f}s")
                else:
                    swap_results.append({
                        "model": model,
                        "success": False
                    })
            
            self.results["model_swapping"] = swap_results
    
    async def make_request(self, session, endpoint, data):
        """Make HTTP request with error handling"""
        try:
            async with session.post(f"{self.base_url}{endpoint}", json=data, timeout=60) as response:
                return response.status == 200
        except:
            return False
    
    async def get_status(self, session):
        """Get server status"""
        try:
            async with session.get(f"{self.base_url}/status", timeout=10) as response:
                if response.status == 200:
                    return await response.json()
        except:
            pass
        return None
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print(f"\n📊 PERFORMANCE REPORT")
        print("=" * 50)
        
        # Throughput summary
        if "throughput" in self.results:
            throughput = self.results["throughput"]
            print(f"\n🚀 Throughput Performance:")
            print(f"  Requests/second: {throughput['requests_per_second']:.2f}")
            print(f"  Average response time: {throughput['avg_response_time']:.2f}s")
            print(f"  P95 response time: {throughput['p95_response_time']:.2f}s")
        
        # Latency summary
        if "latency" in self.results:
            latency = self.results["latency"]
            print(f"\n⏱️ Latency Performance:")
            print(f"  Mean: {latency['mean']:.2f}s")
            print(f"  Median: {latency['median']:.2f}s")
            print(f"  P95: {latency['p95']:.2f}s")
            print(f"  P99: {latency['p99']:.2f}s")
        
        # Concurrent load summary
        if "concurrent_load" in self.results:
            print(f"\n🔄 Concurrent Load Performance:")
            for result in self.results["concurrent_load"]:
                print(f"  {result['concurrency']} concurrent: {result['success_rate']*100:.1f}% success, {result['throughput']:.2f} req/s")
        
        # Memory efficiency summary
        if "memory_efficiency" in self.results:
            memory = self.results["memory_efficiency"]
            print(f"\n💾 Memory Efficiency:")
            print(f"  Peak memory usage: {memory['max_memory_gb']:.2f}GB")
            print(f"  Memory growth: {memory['memory_growth']:.2f}GB")
            print(f"  Memory variance: {memory['memory_variance']:.4f}")
        
        # Model swapping summary
        if "model_swapping" in self.results:
            print(f"\n🔄 Model Swapping Performance:")
            for result in self.results["model_swapping"]:
                if result["success"]:
                    print(f"  {result['model']}: Load {result['load_time']:.1f}s, Inference {result['inference_time']:.2f}s")
        
        # Performance recommendations
        self.generate_recommendations()
        
        # Save results
        timestamp = int(time.time())
        with open(f"benchmark_results_{timestamp}.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to benchmark_results_{timestamp}.json")
    
    def generate_recommendations(self):
        """Generate performance optimization recommendations"""
        print(f"\n💡 Performance Recommendations:")
        
        recommendations = []
        
        # Throughput recommendations
        if "throughput" in self.results:
            throughput = self.results["throughput"]["requests_per_second"]
            if throughput < 5:
                recommendations.append("Low throughput detected. Consider optimizing model size or batch processing.")
            elif throughput > 15:
                recommendations.append("Excellent throughput! System is well optimized.")
        
        # Latency recommendations
        if "latency" in self.results:
            p95_latency = self.results["latency"]["p95"]
            if p95_latency > 5:
                recommendations.append("High P95 latency. Consider model caching or smaller models.")
            elif p95_latency < 2:
                recommendations.append("Excellent latency performance!")
        
        # Memory recommendations
        if "memory_efficiency" in self.results:
            memory_growth = self.results["memory_efficiency"]["memory_growth"]
            if memory_growth > 1:
                recommendations.append("Significant memory growth detected. Check for memory leaks.")
            elif memory_growth < 0.1:
                recommendations.append("Excellent memory efficiency!")
        
        # Concurrent load recommendations
        if "concurrent_load" in self.results:
            high_concurrency = [r for r in self.results["concurrent_load"] if r["concurrency"] >= 8]
            if high_concurrency and high_concurrency[-1]["success_rate"] < 0.8:
                recommendations.append("Poor performance under high concurrency. Consider load balancing.")
        
        if not recommendations:
            recommendations.append("System performance is within acceptable ranges.")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

class SystemValidator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def validate_system_requirements(self):
        """Validate system meets minimum requirements"""
        print("🔍 SYSTEM VALIDATION")
        print("=" * 30)
        
        # Check available memory
        memory = psutil.virtual_memory()
        print(f"RAM: {memory.total / 1024**3:.1f}GB total, {memory.available / 1024**3:.1f}GB available")
        
        if memory.available < 2 * 1024**3:  # Less than 2GB available
            print("⚠️  Warning: Low available memory may impact performance")
        
        # Check swap
        swap = psutil.swap_memory()
        print(f"Swap: {swap.total / 1024**3:.1f}GB total, {swap.free / 1024**3:.1f}GB free")
        
        if swap.total < 10 * 1024**3:  # Less than 10GB swap
            print("⚠️  Warning: Insufficient swap space for large models")
        
        # Check CPU
        cpu_count = psutil.cpu_count()
        print(f"CPU: {cpu_count} cores")
        
        # Check disk space
        disk = psutil.disk_usage('/')
        print(f"Disk: {disk.free / 1024**3:.1f}GB free")
        
        if disk.free < 20 * 1024**3:  # Less than 20GB free
            print("⚠️  Warning: Low disk space may impact model caching")
        
        print("✅ System validation complete")

async def main():
    """Run complete benchmark suite"""
    validator = SystemValidator()
    validator.validate_system_requirements()
    
    benchmark = PerformanceBenchmark()
    await benchmark.run_benchmarks()

if __name__ == "__main__":
    asyncio.run(main())
