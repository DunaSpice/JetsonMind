#!/usr/bin/env python3
import asyncio
import requests
import time
import json
import psutil
import threading
import concurrent.futures
from datetime import datetime
import statistics

class TestRunner:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        self.start_time = None
        
    def run_all_tests(self):
        """Execute complete test suite"""
        print("🧪 ENHANCED AI SERVER TEST SUITE")
        print("=" * 50)
        
        self.start_time = time.time()
        
        # Phase 1: Unit Tests
        print("\n📋 Phase 1: Unit Tests")
        self.test_health_check()
        self.test_status_endpoint()
        self.test_models_endpoint()
        
        # Phase 2: Integration Tests  
        print("\n🔗 Phase 2: Integration Tests")
        self.test_single_inference()
        self.test_batch_inference()
        self.test_model_loading()
        
        # Phase 3: Performance Tests
        print("\n⚡ Phase 3: Performance Tests")
        self.test_response_times()
        self.test_concurrent_requests()
        self.test_memory_usage()
        
        # Phase 4: Stress Tests
        print("\n💪 Phase 4: Stress Tests")
        self.test_high_load()
        self.test_memory_pressure()
        
        # Phase 5: Production Tests
        print("\n🏭 Phase 5: Production Tests")
        self.test_edge_cases()
        self.test_long_running()
        
        # Generate report
        self.generate_report()
        
    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            
            self.results["health_check"] = {"status": "PASS", "response_time": response.elapsed.total_seconds()}
            print("  ✅ Health check: PASS")
            
        except Exception as e:
            self.results["health_check"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Health check: FAIL - {e}")
    
    def test_status_endpoint(self):
        """Test system status endpoint"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=10)
            assert response.status_code == 200
            data = response.json()
            
            # Validate required fields
            required_fields = ["active_models", "memory_usage_gb", "memory_budget_gb"]
            for field in required_fields:
                assert field in data
            
            self.results["status_endpoint"] = {
                "status": "PASS", 
                "active_models": len(data["active_models"]),
                "memory_usage": data["memory_usage_gb"]
            }
            print(f"  ✅ Status endpoint: PASS ({len(data['active_models'])} models active)")
            
        except Exception as e:
            self.results["status_endpoint"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Status endpoint: FAIL - {e}")
    
    def test_models_endpoint(self):
        """Test models information endpoint"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            assert response.status_code == 200
            data = response.json()
            
            assert "active_models" in data
            assert "model_capabilities" in data
            
            self.results["models_endpoint"] = {
                "status": "PASS",
                "active_count": len(data["active_models"]),
                "capabilities_count": len(data["model_capabilities"])
            }
            print(f"  ✅ Models endpoint: PASS")
            
        except Exception as e:
            self.results["models_endpoint"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Models endpoint: FAIL - {e}")
    
    def test_single_inference(self):
        """Test single inference functionality"""
        try:
            test_request = {
                "prompt": "What is 2+2?",
                "max_length": 20
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/inference", json=test_request, timeout=30)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            data = response.json()
            
            required_fields = ["response", "model_used", "inference_time", "tokens_per_second"]
            for field in required_fields:
                assert field in data
            
            assert len(data["response"]) > 0
            assert data["tokens_per_second"] > 0
            
            self.results["single_inference"] = {
                "status": "PASS",
                "response_time": response_time,
                "model_used": data["model_used"],
                "tokens_per_second": data["tokens_per_second"]
            }
            print(f"  ✅ Single inference: PASS ({data['tokens_per_second']:.1f} tok/s)")
            
        except Exception as e:
            self.results["single_inference"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Single inference: FAIL - {e}")
    
    def test_batch_inference(self):
        """Test batch inference functionality"""
        try:
            test_request = {
                "prompts": [
                    "Hello world",
                    "What is AI?", 
                    "Count to 5"
                ]
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/batch_inference", json=test_request, timeout=60)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            data = response.json()
            
            assert "results" in data
            assert len(data["results"]) == 3
            assert "total_time" in data
            
            self.results["batch_inference"] = {
                "status": "PASS",
                "response_time": response_time,
                "batch_size": len(data["results"]),
                "avg_time_per_request": data.get("avg_time_per_request", 0)
            }
            print(f"  ✅ Batch inference: PASS ({len(data['results'])} requests)")
            
        except Exception as e:
            self.results["batch_inference"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Batch inference: FAIL - {e}")
    
    def test_model_loading(self):
        """Test explicit model loading"""
        try:
            test_request = {
                "model_name": "Qwen/Qwen2.5-0.5B-Instruct",
                "priority": "normal"
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/load_model", json=test_request, timeout=120)
            load_time = time.time() - start_time
            
            assert response.status_code == 200
            data = response.json()
            assert "load_time" in data
            
            self.results["model_loading"] = {
                "status": "PASS",
                "load_time": load_time,
                "reported_load_time": data["load_time"]
            }
            print(f"  ✅ Model loading: PASS ({load_time:.1f}s)")
            
        except Exception as e:
            self.results["model_loading"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Model loading: FAIL - {e}")
    
    def test_response_times(self):
        """Test response time consistency"""
        try:
            times = []
            test_request = {"prompt": "Quick test", "max_length": 10}
            
            for i in range(5):
                start_time = time.time()
                response = requests.post(f"{self.base_url}/inference", json=test_request, timeout=30)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    times.append(response_time)
            
            if times:
                avg_time = statistics.mean(times)
                std_dev = statistics.stdev(times) if len(times) > 1 else 0
                
                self.results["response_times"] = {
                    "status": "PASS",
                    "avg_response_time": avg_time,
                    "std_deviation": std_dev,
                    "min_time": min(times),
                    "max_time": max(times)
                }
                print(f"  ✅ Response times: PASS (avg: {avg_time:.2f}s, std: {std_dev:.2f}s)")
            else:
                raise Exception("No successful responses")
                
        except Exception as e:
            self.results["response_times"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Response times: FAIL - {e}")
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        try:
            def make_request():
                test_request = {"prompt": f"Concurrent test {time.time()}", "max_length": 15}
                start_time = time.time()
                response = requests.post(f"{self.base_url}/inference", json=test_request, timeout=60)
                response_time = time.time() - start_time
                return response.status_code == 200, response_time
            
            # Test with 5 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful = sum(1 for success, _ in results if success)
            times = [time for success, time in results if success]
            
            if successful >= 3:  # At least 60% success rate
                self.results["concurrent_requests"] = {
                    "status": "PASS",
                    "successful_requests": successful,
                    "total_requests": 5,
                    "avg_response_time": statistics.mean(times) if times else 0
                }
                print(f"  ✅ Concurrent requests: PASS ({successful}/5 successful)")
            else:
                raise Exception(f"Only {successful}/5 requests successful")
                
        except Exception as e:
            self.results["concurrent_requests"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Concurrent requests: FAIL - {e}")
    
    def test_memory_usage(self):
        """Test memory usage patterns"""
        try:
            # Get initial memory
            initial_status = requests.get(f"{self.base_url}/status").json()
            initial_memory = initial_status["memory_usage_gb"]
            
            # Make several requests
            for i in range(3):
                test_request = {"prompt": f"Memory test {i}", "max_length": 20}
                requests.post(f"{self.base_url}/inference", json=test_request, timeout=30)
            
            # Check final memory
            final_status = requests.get(f"{self.base_url}/status").json()
            final_memory = final_status["memory_usage_gb"]
            
            memory_increase = final_memory - initial_memory
            
            self.results["memory_usage"] = {
                "status": "PASS",
                "initial_memory_gb": initial_memory,
                "final_memory_gb": final_memory,
                "memory_increase_gb": memory_increase,
                "memory_budget_gb": final_status["memory_budget_gb"]
            }
            print(f"  ✅ Memory usage: PASS (increase: {memory_increase:.2f}GB)")
            
        except Exception as e:
            self.results["memory_usage"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Memory usage: FAIL - {e}")
    
    def test_high_load(self):
        """Test system under high load"""
        try:
            def make_batch_request():
                test_request = {
                    "prompts": [f"Load test {i}" for i in range(3)]
                }
                response = requests.post(f"{self.base_url}/batch_inference", json=test_request, timeout=120)
                return response.status_code == 200
            
            # Send 3 concurrent batch requests (9 total inferences)
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(make_batch_request) for _ in range(3)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful = sum(results)
            
            if successful >= 2:  # At least 2/3 batch requests successful
                self.results["high_load"] = {
                    "status": "PASS",
                    "successful_batches": successful,
                    "total_batches": 3
                }
                print(f"  ✅ High load: PASS ({successful}/3 batches successful)")
            else:
                raise Exception(f"Only {successful}/3 batches successful")
                
        except Exception as e:
            self.results["high_load"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ High load: FAIL - {e}")
    
    def test_memory_pressure(self):
        """Test behavior under memory pressure"""
        try:
            # Try to load a larger model to create memory pressure
            test_request = {
                "model_name": "Qwen/Qwen2.5-1.5B-Instruct",
                "priority": "normal"
            }
            
            response = requests.post(f"{self.base_url}/load_model", json=test_request, timeout=180)
            
            # Check if system is still responsive
            status_response = requests.get(f"{self.base_url}/status", timeout=10)
            
            if response.status_code == 200 and status_response.status_code == 200:
                status_data = status_response.json()
                
                self.results["memory_pressure"] = {
                    "status": "PASS",
                    "memory_usage_gb": status_data["memory_usage_gb"],
                    "active_models": len(status_data["active_models"])
                }
                print(f"  ✅ Memory pressure: PASS (system responsive)")
            else:
                raise Exception("System not responsive under memory pressure")
                
        except Exception as e:
            self.results["memory_pressure"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Memory pressure: FAIL - {e}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        try:
            edge_cases = [
                {"prompt": "", "max_length": 10},  # Empty prompt
                {"prompt": "A" * 1000, "max_length": 5},  # Very long prompt
                {"prompt": "Test", "max_length": 0},  # Zero max length
            ]
            
            results = []
            for case in edge_cases:
                try:
                    response = requests.post(f"{self.base_url}/inference", json=case, timeout=30)
                    results.append(response.status_code in [200, 400, 422])  # Accept valid error codes
                except:
                    results.append(False)
            
            successful = sum(results)
            
            self.results["edge_cases"] = {
                "status": "PASS" if successful >= 2 else "FAIL",
                "successful_cases": successful,
                "total_cases": len(edge_cases)
            }
            print(f"  ✅ Edge cases: {'PASS' if successful >= 2 else 'FAIL'} ({successful}/{len(edge_cases)})")
            
        except Exception as e:
            self.results["edge_cases"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Edge cases: FAIL - {e}")
    
    def test_long_running(self):
        """Test system stability over time"""
        try:
            start_time = time.time()
            successful_requests = 0
            
            # Run requests for 30 seconds
            while time.time() - start_time < 30:
                try:
                    test_request = {"prompt": "Stability test", "max_length": 10}
                    response = requests.post(f"{self.base_url}/inference", json=test_request, timeout=15)
                    if response.status_code == 200:
                        successful_requests += 1
                    time.sleep(2)  # Wait between requests
                except:
                    pass
            
            duration = time.time() - start_time
            
            self.results["long_running"] = {
                "status": "PASS" if successful_requests >= 10 else "FAIL",
                "duration": duration,
                "successful_requests": successful_requests,
                "requests_per_second": successful_requests / duration
            }
            print(f"  ✅ Long running: {'PASS' if successful_requests >= 10 else 'FAIL'} ({successful_requests} requests)")
            
        except Exception as e:
            self.results["long_running"] = {"status": "FAIL", "error": str(e)}
            print(f"  ❌ Long running: FAIL - {e}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        
        passed_tests = sum(1 for test in self.results.values() if test.get("status") == "PASS")
        total_tests = len(self.results)
        
        print(f"\n📊 TEST REPORT")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total Time: {total_time:.1f}s")
        
        print(f"\n📈 PERFORMANCE SUMMARY")
        print("-" * 30)
        
        if "single_inference" in self.results and self.results["single_inference"]["status"] == "PASS":
            print(f"Single Inference: {self.results['single_inference']['tokens_per_second']:.1f} tok/s")
        
        if "response_times" in self.results and self.results["response_times"]["status"] == "PASS":
            print(f"Avg Response Time: {self.results['response_times']['avg_response_time']:.2f}s")
        
        if "memory_usage" in self.results and self.results["memory_usage"]["status"] == "PASS":
            print(f"Memory Usage: {self.results['memory_usage']['final_memory_gb']:.1f}GB")
        
        # Save detailed results
        with open(f"test_results_{int(time.time())}.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to test_results_{int(time.time())}.json")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} tests failed. Review results before deployment.")

if __name__ == "__main__":
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"Testing server at: {base_url}")
    print("Make sure the server is running before starting tests.")
    input("Press Enter to continue...")
    
    runner = TestRunner(base_url)
    runner.run_all_tests()
