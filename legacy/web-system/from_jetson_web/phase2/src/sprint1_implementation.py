#!/usr/bin/env python3
"""
PHASE 2 - SPRINT 1: Enhanced Model Selection
Control-driven implementation with continuous validation
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import time
import logging
import asyncio

# Control framework
class ControlMetrics:
    def __init__(self):
        self.baseline_response_time = 0.8  # Phase 1 baseline
        self.max_overhead_ms = 10
        self.performance_alerts = []
    
    def validate_performance(self, duration_ms):
        if duration_ms > self.max_overhead_ms:
            self.performance_alerts.append(f"Overhead exceeded: {duration_ms:.1f}ms")
            return False
        return True

# Enhanced API Schema (backward compatible)
class EnhancedInferenceRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 20
    temperature: Optional[float] = 0.7
    
    # NEW: Model selection options (all optional for backward compatibility)
    model: Optional[str] = None              # Manual selection
    auto_select: Optional[bool] = None       # Auto selection  
    preferred_model: Optional[str] = None    # Hybrid mode
    fallback_mode: Optional[str] = "auto"    # Fallback strategy

class ModelSelectionResponse(BaseModel):
    selected_model: str
    selection_mode: str
    selection_time_ms: float
    reasoning: Optional[str] = None

# Model Selection Engine
class EnhancedModelSelector:
    def __init__(self, available_models: dict, control_metrics: ControlMetrics):
        self.available_models = available_models
        self.control_metrics = control_metrics
        self.selection_stats = {"manual": 0, "auto": 0, "hybrid": 0}
    
    async def select_model(self, request: EnhancedInferenceRequest) -> ModelSelectionResponse:
        """
        Enhanced model selection with control validation
        """
        start_time = time.time()
        
        # Control Point 1: Validate request
        if not self.available_models:
            raise HTTPException(500, "No models available")
        
        # Selection Logic
        if request.model:
            # Manual Selection (fastest path)
            result = await self._manual_selection(request.model)
            self.selection_stats["manual"] += 1
            
        elif request.preferred_model:
            # Hybrid Selection
            result = await self._hybrid_selection(request.preferred_model, request.prompt)
            self.selection_stats["hybrid"] += 1
            
        else:
            # Auto Selection (default for backward compatibility)
            result = await self._auto_selection(request.prompt)
            self.selection_stats["auto"] += 1
        
        # Control Point 2: Validate performance
        selection_time_ms = (time.time() - start_time) * 1000
        if not self.control_metrics.validate_performance(selection_time_ms):
            logging.warning(f"Selection overhead exceeded threshold: {selection_time_ms:.1f}ms")
        
        result.selection_time_ms = selection_time_ms
        return result
    
    async def _manual_selection(self, model_name: str) -> ModelSelectionResponse:
        """Manual model selection - direct and fast"""
        if model_name not in self.available_models:
            raise HTTPException(404, f"Model '{model_name}' not available. Available: {list(self.available_models.keys())}")
        
        return ModelSelectionResponse(
            selected_model=model_name,
            selection_mode="manual",
            selection_time_ms=0,  # Will be set by caller
            reasoning=f"User specified model: {model_name}"
        )
    
    async def _auto_selection(self, prompt: str) -> ModelSelectionResponse:
        """Intelligent auto selection"""
        # Simple intelligence for Sprint 1 (will enhance in Sprint 2)
        
        # For now, use first available model (Phase 1 behavior)
        selected_model = list(self.available_models.keys())[0]
        
        # Future: Add prompt analysis here
        reasoning = "Auto-selected first available model (Phase 1 compatibility)"
        
        return ModelSelectionResponse(
            selected_model=selected_model,
            selection_mode="auto",
            selection_time_ms=0,  # Will be set by caller
            reasoning=reasoning
        )
    
    async def _hybrid_selection(self, preferred_model: str, prompt: str) -> ModelSelectionResponse:
        """Hybrid selection with fallback"""
        if preferred_model in self.available_models:
            return ModelSelectionResponse(
                selected_model=preferred_model,
                selection_mode="hybrid_preferred",
                selection_time_ms=0,  # Will be set by caller
                reasoning=f"Used preferred model: {preferred_model}"
            )
        else:
            # Fallback to auto selection
            auto_result = await self._auto_selection(prompt)
            auto_result.selection_mode = "hybrid_fallback"
            auto_result.reasoning = f"Preferred model '{preferred_model}' unavailable, fell back to auto selection"
            return auto_result

# Enhanced Server Implementation
class EnhancedAIServer:
    def __init__(self):
        self.app = FastAPI(title="Enhanced AI Server - Phase 2", version="2.0.0")
        self.control_metrics = ControlMetrics()
        self.models = {}  # Will be populated from Phase 1
        self.model_selector = None
        
        # Setup routes
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.on_event("startup")
        async def startup():
            # Initialize model selector
            self.model_selector = EnhancedModelSelector(self.models, self.control_metrics)
            logging.info("Enhanced AI Server Phase 2 started")
        
        @self.app.get("/health")
        def health():
            return {
                "status": "healthy",
                "version": "2.0.0",
                "phase": "2",
                "timestamp": time.time()
            }
        
        @self.app.post("/inference")
        async def enhanced_inference(request: EnhancedInferenceRequest):
            """Enhanced inference with flexible model selection"""
            
            # Control Point: Performance monitoring
            total_start = time.time()
            
            try:
                # Step 1: Model Selection
                selection_result = await self.model_selector.select_model(request)
                
                # Step 2: Execute Inference (using Phase 1 logic)
                inference_result = await self._execute_inference(
                    selection_result.selected_model, 
                    request
                )
                
                # Step 3: Combine results
                total_time = time.time() - total_start
                
                # Control Point: Validate total performance
                if total_time > self.control_metrics.baseline_response_time * 1.2:
                    logging.warning(f"Total response time exceeded baseline: {total_time:.2f}s")
                
                return {
                    **inference_result,
                    "selection_info": {
                        "selected_model": selection_result.selected_model,
                        "selection_mode": selection_result.selection_mode,
                        "selection_time_ms": selection_result.selection_time_ms,
                        "reasoning": selection_result.reasoning
                    },
                    "total_time": total_time
                }
                
            except Exception as e:
                logging.error(f"Enhanced inference failed: {e}")
                raise HTTPException(500, f"Inference failed: {str(e)}")
        
        @self.app.get("/selection_stats")
        def get_selection_stats():
            """Get model selection statistics"""
            if self.model_selector:
                return {
                    "selection_counts": self.model_selector.selection_stats,
                    "performance_alerts": self.control_metrics.performance_alerts[-10:],  # Last 10 alerts
                    "available_models": list(self.models.keys())
                }
            return {"error": "Model selector not initialized"}
    
    async def _execute_inference(self, model_name: str, request: EnhancedInferenceRequest):
        """Execute inference using Phase 1 logic (placeholder)"""
        # This will integrate with Phase 1 inference engine
        
        # Placeholder implementation
        await asyncio.sleep(0.1)  # Simulate inference time
        
        return {
            "response": f"Enhanced response from {model_name}: {request.prompt}",
            "model_used": model_name,
            "inference_time": 0.1,
            "tokens_generated": 10,
            "tokens_per_second": 100.0,
            "timestamp": time.time()
        }

# Control Testing Framework
class Sprint1ControlTests:
    def __init__(self, server: EnhancedAIServer):
        self.server = server
        self.test_results = []
    
    async def run_control_tests(self):
        """Run comprehensive control tests for Sprint 1"""
        
        print("🧪 SPRINT 1 CONTROL TESTS")
        print("=" * 40)
        
        # Test 1: Backward Compatibility
        await self._test_backward_compatibility()
        
        # Test 2: Manual Selection
        await self._test_manual_selection()
        
        # Test 3: Auto Selection
        await self._test_auto_selection()
        
        # Test 4: Hybrid Selection
        await self._test_hybrid_selection()
        
        # Test 5: Performance Control
        await self._test_performance_control()
        
        # Test 6: Error Handling
        await self._test_error_handling()
        
        return self._generate_control_report()
    
    async def _test_backward_compatibility(self):
        """Ensure Phase 1 API still works"""
        print("Testing backward compatibility...")
        
        # Simulate Phase 1 request (no selection parameters)
        request = EnhancedInferenceRequest(prompt="test")
        
        try:
            # This should work exactly like Phase 1
            result = await self.server.model_selector.select_model(request)
            assert result.selection_mode == "auto"
            self.test_results.append(("backward_compatibility", "PASS"))
            print("✅ Backward compatibility: PASS")
        except Exception as e:
            self.test_results.append(("backward_compatibility", f"FAIL: {e}"))
            print(f"❌ Backward compatibility: FAIL - {e}")
    
    async def _test_manual_selection(self):
        """Test manual model selection"""
        print("Testing manual selection...")
        
        # Add a test model
        self.server.models["test_model"] = {"loaded": True}
        self.server.model_selector.available_models = self.server.models
        
        request = EnhancedInferenceRequest(prompt="test", model="test_model")
        
        try:
            result = await self.server.model_selector.select_model(request)
            assert result.selected_model == "test_model"
            assert result.selection_mode == "manual"
            self.test_results.append(("manual_selection", "PASS"))
            print("✅ Manual selection: PASS")
        except Exception as e:
            self.test_results.append(("manual_selection", f"FAIL: {e}"))
            print(f"❌ Manual selection: FAIL - {e}")
    
    async def _test_auto_selection(self):
        """Test auto selection"""
        print("Testing auto selection...")
        
        request = EnhancedInferenceRequest(prompt="test", auto_select=True)
        
        try:
            result = await self.server.model_selector.select_model(request)
            assert result.selection_mode == "auto"
            self.test_results.append(("auto_selection", "PASS"))
            print("✅ Auto selection: PASS")
        except Exception as e:
            self.test_results.append(("auto_selection", f"FAIL: {e}"))
            print(f"❌ Auto selection: FAIL - {e}")
    
    async def _test_hybrid_selection(self):
        """Test hybrid selection"""
        print("Testing hybrid selection...")
        
        # Test preferred model available
        request = EnhancedInferenceRequest(prompt="test", preferred_model="test_model")
        
        try:
            result = await self.server.model_selector.select_model(request)
            assert result.selected_model == "test_model"
            assert result.selection_mode == "hybrid_preferred"
            self.test_results.append(("hybrid_selection", "PASS"))
            print("✅ Hybrid selection: PASS")
        except Exception as e:
            self.test_results.append(("hybrid_selection", f"FAIL: {e}"))
            print(f"❌ Hybrid selection: FAIL - {e}")
    
    async def _test_performance_control(self):
        """Test performance control thresholds"""
        print("Testing performance control...")
        
        # Test that selection is fast enough
        start_time = time.time()
        request = EnhancedInferenceRequest(prompt="test", auto_select=True)
        
        try:
            result = await self.server.model_selector.select_model(request)
            selection_time_ms = (time.time() - start_time) * 1000
            
            assert selection_time_ms < 10  # Must be under 10ms
            self.test_results.append(("performance_control", "PASS"))
            print(f"✅ Performance control: PASS ({selection_time_ms:.1f}ms)")
        except Exception as e:
            self.test_results.append(("performance_control", f"FAIL: {e}"))
            print(f"❌ Performance control: FAIL - {e}")
    
    async def _test_error_handling(self):
        """Test error handling"""
        print("Testing error handling...")
        
        # Test invalid model
        request = EnhancedInferenceRequest(prompt="test", model="nonexistent_model")
        
        try:
            await self.server.model_selector.select_model(request)
            self.test_results.append(("error_handling", "FAIL: Should have raised exception"))
            print("❌ Error handling: FAIL - Should have raised exception")
        except HTTPException as e:
            if e.status_code == 404:
                self.test_results.append(("error_handling", "PASS"))
                print("✅ Error handling: PASS")
            else:
                self.test_results.append(("error_handling", f"FAIL: Wrong status code {e.status_code}"))
                print(f"❌ Error handling: FAIL - Wrong status code {e.status_code}")
        except Exception as e:
            self.test_results.append(("error_handling", f"FAIL: {e}"))
            print(f"❌ Error handling: FAIL - {e}")
    
    def _generate_control_report(self):
        """Generate control test report"""
        passed = sum(1 for _, result in self.test_results if result == "PASS")
        total = len(self.test_results)
        
        print(f"\n📊 CONTROL TEST RESULTS: {passed}/{total} PASSED")
        
        if passed == total:
            print("✅ ALL CONTROL TESTS PASSED - READY FOR INTEGRATION")
            return True
        else:
            print("❌ SOME CONTROL TESTS FAILED - DO NOT INTEGRATE")
            for test_name, result in self.test_results:
                if result != "PASS":
                    print(f"   {test_name}: {result}")
            return False

# Main execution for Sprint 1
async def main():
    """Sprint 1 development execution with control"""
    
    print("🚀 PHASE 2 - SPRINT 1: Enhanced Model Selection")
    print("=" * 50)
    
    # Step 1: Initialize enhanced server
    server = EnhancedAIServer()
    
    # Step 2: Run control tests
    tester = Sprint1ControlTests(server)
    control_passed = await tester.run_control_tests()
    
    if control_passed:
        print("\n🎉 SPRINT 1 CONTROL VALIDATION COMPLETE")
        print("✅ Ready for integration with Phase 1 system")
        print("✅ All performance thresholds met")
        print("✅ Backward compatibility maintained")
        print("\n🎯 Next: Integrate with Phase 1 and deploy")
    else:
        print("\n🛑 SPRINT 1 CONTROL VALIDATION FAILED")
        print("❌ Do not integrate - fix issues first")
        print("❌ Review failed tests and implement fixes")

if __name__ == "__main__":
    asyncio.run(main())
