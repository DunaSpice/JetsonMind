#!/usr/bin/env python3
"""
PHASE 2 - SPRINT 1: Enhanced Model Selection (Working Implementation)
Control-driven development with immediate validation
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Control Framework
class ControlMetrics:
    def __init__(self):
        self.max_overhead_ms = 10
        self.performance_alerts = []
        self.baseline_response_time = 0.8
    
    def validate_performance(self, duration_ms: float) -> bool:
        if duration_ms > self.max_overhead_ms:
            alert = f"Selection overhead exceeded: {duration_ms:.1f}ms > {self.max_overhead_ms}ms"
            self.performance_alerts.append(alert)
            logger.warning(alert)
            return False
        return True

# Enhanced Request Model
class EnhancedRequest:
    def __init__(self, prompt: str, model: str = None, auto_select: bool = None, 
                 preferred_model: str = None, max_length: int = 20):
        self.prompt = prompt
        self.model = model
        self.auto_select = auto_select
        self.preferred_model = preferred_model
        self.max_length = max_length

# Selection Result
class SelectionResult:
    def __init__(self, selected_model: str, selection_mode: str, 
                 selection_time_ms: float, reasoning: str = ""):
        self.selected_model = selected_model
        self.selection_mode = selection_mode
        self.selection_time_ms = selection_time_ms
        self.reasoning = reasoning

# Enhanced Model Selector
class EnhancedModelSelector:
    def __init__(self, available_models: Dict[str, Any]):
        self.available_models = available_models
        self.selection_stats = {"manual": 0, "auto": 0, "hybrid": 0}
        self.control_metrics = ControlMetrics()
    
    async def select_model(self, request: EnhancedRequest) -> SelectionResult:
        """Enhanced model selection with control validation"""
        start_time = time.time()
        
        # Validate available models
        if not self.available_models:
            raise Exception("No models available")
        
        # Selection Logic
        if request.model:
            # Manual Selection
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
        
        # Control Point: Validate performance
        selection_time_ms = (time.time() - start_time) * 1000
        self.control_metrics.validate_performance(selection_time_ms)
        
        result.selection_time_ms = selection_time_ms
        return result
    
    async def _manual_selection(self, model_name: str) -> SelectionResult:
        """Manual model selection - direct and fast"""
        if model_name not in self.available_models:
            available = list(self.available_models.keys())
            raise Exception(f"Model '{model_name}' not available. Available: {available}")
        
        return SelectionResult(
            selected_model=model_name,
            selection_mode="manual",
            selection_time_ms=0,  # Will be set by caller
            reasoning=f"User specified model: {model_name}"
        )
    
    async def _auto_selection(self, prompt: str) -> SelectionResult:
        """Intelligent auto selection"""
        # Simple intelligence for Sprint 1 (Phase 1 compatibility)
        selected_model = list(self.available_models.keys())[0]
        
        return SelectionResult(
            selected_model=selected_model,
            selection_mode="auto",
            selection_time_ms=0,
            reasoning="Auto-selected first available model (Phase 1 compatibility)"
        )
    
    async def _hybrid_selection(self, preferred_model: str, prompt: str) -> SelectionResult:
        """Hybrid selection with fallback"""
        if preferred_model in self.available_models:
            return SelectionResult(
                selected_model=preferred_model,
                selection_mode="hybrid_preferred",
                selection_time_ms=0,
                reasoning=f"Used preferred model: {preferred_model}"
            )
        else:
            # Fallback to auto selection
            auto_result = await self._auto_selection(prompt)
            auto_result.selection_mode = "hybrid_fallback"
            auto_result.reasoning = f"Preferred '{preferred_model}' unavailable, used auto selection"
            return auto_result

# Control Testing Framework
class Sprint1ControlTests:
    def __init__(self):
        self.test_results = []
        self.available_models = {
            "distilgpt2": {"loaded": True, "size": "336MB"},
            "gpt2": {"loaded": True, "size": "523MB"}
        }
        self.selector = EnhancedModelSelector(self.available_models)
    
    async def run_all_tests(self):
        """Run comprehensive control tests"""
        
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
        
        return self._generate_report()
    
    async def _test_backward_compatibility(self):
        """Ensure Phase 1 API still works"""
        print("1. Testing backward compatibility...")
        
        try:
            # Phase 1 style request (no selection parameters)
            request = EnhancedRequest(prompt="test backward compatibility")
            result = await self.selector.select_model(request)
            
            assert result.selection_mode == "auto"
            assert result.selected_model in self.available_models
            
            self.test_results.append(("backward_compatibility", "PASS"))
            print("   ✅ PASS - Phase 1 behavior maintained")
            
        except Exception as e:
            self.test_results.append(("backward_compatibility", f"FAIL: {e}"))
            print(f"   ❌ FAIL - {e}")
    
    async def _test_manual_selection(self):
        """Test manual model selection"""
        print("2. Testing manual selection...")
        
        try:
            # Test valid model
            request = EnhancedRequest(prompt="test manual", model="gpt2")
            result = await self.selector.select_model(request)
            
            assert result.selected_model == "gpt2"
            assert result.selection_mode == "manual"
            assert result.selection_time_ms < 10  # Performance control
            
            self.test_results.append(("manual_selection", "PASS"))
            print(f"   ✅ PASS - Selected {result.selected_model} in {result.selection_time_ms:.1f}ms")
            
        except Exception as e:
            self.test_results.append(("manual_selection", f"FAIL: {e}"))
            print(f"   ❌ FAIL - {e}")
    
    async def _test_auto_selection(self):
        """Test auto selection"""
        print("3. Testing auto selection...")
        
        try:
            request = EnhancedRequest(prompt="test auto", auto_select=True)
            result = await self.selector.select_model(request)
            
            assert result.selection_mode == "auto"
            assert result.selected_model in self.available_models
            assert result.selection_time_ms < 10
            
            self.test_results.append(("auto_selection", "PASS"))
            print(f"   ✅ PASS - Auto-selected {result.selected_model} in {result.selection_time_ms:.1f}ms")
            
        except Exception as e:
            self.test_results.append(("auto_selection", f"FAIL: {e}"))
            print(f"   ❌ FAIL - {e}")
    
    async def _test_hybrid_selection(self):
        """Test hybrid selection"""
        print("4. Testing hybrid selection...")
        
        try:
            # Test preferred model available
            request = EnhancedRequest(prompt="test hybrid", preferred_model="distilgpt2")
            result = await self.selector.select_model(request)
            
            assert result.selected_model == "distilgpt2"
            assert result.selection_mode == "hybrid_preferred"
            
            # Test preferred model unavailable (fallback)
            request2 = EnhancedRequest(prompt="test hybrid fallback", preferred_model="nonexistent")
            result2 = await self.selector.select_model(request2)
            
            assert result2.selection_mode == "hybrid_fallback"
            assert result2.selected_model in self.available_models
            
            self.test_results.append(("hybrid_selection", "PASS"))
            print(f"   ✅ PASS - Preferred: {result.selected_model}, Fallback: {result2.selected_model}")
            
        except Exception as e:
            self.test_results.append(("hybrid_selection", f"FAIL: {e}"))
            print(f"   ❌ FAIL - {e}")
    
    async def _test_performance_control(self):
        """Test performance control thresholds"""
        print("5. Testing performance control...")
        
        try:
            # Run multiple selections and measure performance
            times = []
            for i in range(5):
                start = time.time()
                request = EnhancedRequest(prompt=f"performance test {i}", auto_select=True)
                result = await self.selector.select_model(request)
                duration_ms = (time.time() - start) * 1000
                times.append(duration_ms)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            assert avg_time < 5  # Average should be very fast
            assert max_time < 10  # No single selection should exceed 10ms
            
            self.test_results.append(("performance_control", "PASS"))
            print(f"   ✅ PASS - Avg: {avg_time:.1f}ms, Max: {max_time:.1f}ms")
            
        except Exception as e:
            self.test_results.append(("performance_control", f"FAIL: {e}"))
            print(f"   ❌ FAIL - {e}")
    
    async def _test_error_handling(self):
        """Test error handling"""
        print("6. Testing error handling...")
        
        try:
            # Test invalid model
            request = EnhancedRequest(prompt="test error", model="nonexistent_model")
            
            try:
                await self.selector.select_model(request)
                # Should not reach here
                self.test_results.append(("error_handling", "FAIL: Should have raised exception"))
                print("   ❌ FAIL - Should have raised exception for invalid model")
            except Exception as expected_error:
                # This is expected
                assert "not available" in str(expected_error)
                self.test_results.append(("error_handling", "PASS"))
                print("   ✅ PASS - Properly handled invalid model error")
            
        except Exception as e:
            self.test_results.append(("error_handling", f"FAIL: {e}"))
            print(f"   ❌ FAIL - {e}")
    
    def _generate_report(self):
        """Generate comprehensive test report"""
        passed = sum(1 for _, result in self.test_results if result == "PASS")
        total = len(self.test_results)
        
        print(f"\n📊 SPRINT 1 CONTROL TEST RESULTS")
        print("=" * 40)
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show selection statistics
        print(f"\nSelection Statistics:")
        for mode, count in self.selector.selection_stats.items():
            print(f"  {mode}: {count} selections")
        
        # Show performance alerts
        if self.selector.control_metrics.performance_alerts:
            print(f"\nPerformance Alerts:")
            for alert in self.selector.control_metrics.performance_alerts:
                print(f"  ⚠️ {alert}")
        else:
            print(f"\n✅ No performance alerts - all selections within thresholds")
        
        # Final assessment
        if passed == total:
            print(f"\n🎉 ALL CONTROL TESTS PASSED")
            print(f"✅ Sprint 1 implementation ready for integration")
            print(f"✅ Backward compatibility maintained")
            print(f"✅ Performance thresholds met")
            print(f"✅ Error handling validated")
            return True
        else:
            print(f"\n🛑 CONTROL TESTS FAILED")
            print(f"❌ Do not integrate - fix issues first")
            for test_name, result in self.test_results:
                if result != "PASS":
                    print(f"   {test_name}: {result}")
            return False

# Demonstration of Enhanced Selection
async def demonstrate_selection_modes():
    """Demonstrate all three selection modes"""
    
    print("\n🎯 ENHANCED MODEL SELECTION DEMONSTRATION")
    print("=" * 50)
    
    # Setup
    available_models = {
        "distilgpt2": {"loaded": True, "size": "336MB", "speed": "fast"},
        "gpt2": {"loaded": True, "size": "523MB", "speed": "medium"}
    }
    
    selector = EnhancedModelSelector(available_models)
    
    # Demo 1: Manual Selection
    print("\n1. Manual Selection:")
    request = EnhancedRequest(prompt="Write code", model="gpt2")
    result = await selector.select_model(request)
    print(f"   Request: model='gpt2'")
    print(f"   Result: {result.selected_model} ({result.selection_mode})")
    print(f"   Reasoning: {result.reasoning}")
    print(f"   Time: {result.selection_time_ms:.1f}ms")
    
    # Demo 2: Auto Selection
    print("\n2. Auto Selection:")
    request = EnhancedRequest(prompt="Simple question", auto_select=True)
    result = await selector.select_model(request)
    print(f"   Request: auto_select=True")
    print(f"   Result: {result.selected_model} ({result.selection_mode})")
    print(f"   Reasoning: {result.reasoning}")
    print(f"   Time: {result.selection_time_ms:.1f}ms")
    
    # Demo 3: Hybrid Selection (preferred available)
    print("\n3. Hybrid Selection (preferred available):")
    request = EnhancedRequest(prompt="Creative writing", preferred_model="distilgpt2")
    result = await selector.select_model(request)
    print(f"   Request: preferred_model='distilgpt2'")
    print(f"   Result: {result.selected_model} ({result.selection_mode})")
    print(f"   Reasoning: {result.reasoning}")
    print(f"   Time: {result.selection_time_ms:.1f}ms")
    
    # Demo 4: Hybrid Selection (fallback)
    print("\n4. Hybrid Selection (fallback):")
    request = EnhancedRequest(prompt="Analysis task", preferred_model="nonexistent")
    result = await selector.select_model(request)
    print(f"   Request: preferred_model='nonexistent'")
    print(f"   Result: {result.selected_model} ({result.selection_mode})")
    print(f"   Reasoning: {result.reasoning}")
    print(f"   Time: {result.selection_time_ms:.1f}ms")
    
    # Demo 5: Backward Compatibility
    print("\n5. Backward Compatibility (Phase 1 style):")
    request = EnhancedRequest(prompt="Legacy request")  # No selection parameters
    result = await selector.select_model(request)
    print(f"   Request: (no selection parameters)")
    print(f"   Result: {result.selected_model} ({result.selection_mode})")
    print(f"   Reasoning: {result.reasoning}")
    print(f"   Time: {result.selection_time_ms:.1f}ms")

# Main execution
async def main():
    """Execute Sprint 1 with full control validation"""
    
    print("🚀 PHASE 2 - SPRINT 1: Enhanced Model Selection")
    print("=" * 50)
    print("Control-driven development with continuous validation")
    
    # Step 1: Run control tests
    tester = Sprint1ControlTests()
    control_passed = await tester.run_all_tests()
    
    if control_passed:
        # Step 2: Demonstrate functionality
        await demonstrate_selection_modes()
        
        # Step 3: Final assessment
        print(f"\n🎉 SPRINT 1 COMPLETE - READY FOR INTEGRATION")
        print(f"=" * 50)
        print(f"✅ All control tests passed")
        print(f"✅ Three selection modes implemented:")
        print(f"   • Manual: Direct model specification")
        print(f"   • Auto: Intelligent selection (Phase 1 compatible)")
        print(f"   • Hybrid: Preferred with fallback")
        print(f"✅ Performance within thresholds (<10ms overhead)")
        print(f"✅ Backward compatibility maintained")
        print(f"✅ Comprehensive error handling")
        print(f"\n🎯 Next Step: Integrate with Phase 1 system")
        
    else:
        print(f"\n🛑 SPRINT 1 FAILED CONTROL VALIDATION")
        print(f"❌ Do not proceed to integration")
        print(f"❌ Fix failing tests before continuing")

if __name__ == "__main__":
    asyncio.run(main())
