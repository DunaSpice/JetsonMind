#!/usr/bin/env python3
"""
Phase 2 + Hot Loading Integration
Complete system with live model loading capability
"""

import asyncio
import time
from typing import Dict, Optional
from hot_model_loader import HotModelLoader, LoadStatus
from phase2_complete_integration import Phase2CompleteServer

class Phase2HotLoadServer(Phase2CompleteServer):
    """Phase 2 server enhanced with hot loading"""
    
    def __init__(self):
        super().__init__()
        self.hot_loader = HotModelLoader(self)
    
    def register_hot_loaded_model(self, model_name: str, config: Dict):
        """Register hot-loaded model into main library"""
        from phase2_complete_integration import ModelSpec, ModelTier
        
        # Convert config to ModelSpec
        tier_map = {"ram": ModelTier.RAM, "swap": ModelTier.SWAP, "storage": ModelTier.STORAGE}
        tier = tier_map.get(config.get("tier", "storage"), ModelTier.STORAGE)
        
        # Estimate load time based on size and tier
        size_gb = config.get("size_gb", 1.0)
        if tier == ModelTier.RAM:
            load_time = size_gb * 0.1  # 0.1s per GB for RAM
        else:
            load_time = size_gb * 0.5  # 0.5s per GB for swap
        
        model_spec = ModelSpec(
            name=model_name,
            size_gb=size_gb,
            tier=tier,
            load_time_estimate=load_time,
            capabilities=config.get("capabilities", ["text-generation"])
        )
        
        self.model_library[model_name] = model_spec
        print(f"✅ Hot loaded '{model_name}' into Phase 2 system")
    
    def is_model_safe_to_load_from_config(self, config: Dict) -> tuple:
        """Safety check for hot loading"""
        size_gb = config.get("size_gb", 0)
        tier = config.get("tier", "storage")
        
        if tier == "storage" or size_gb > 10.5:
            return False, f"Model too large: {size_gb}GB"
        
        # Use Phase 2 safety logic
        from phase2_complete_integration import ModelSpec, ModelTier
        tier_enum = ModelTier.RAM if tier == "ram" else ModelTier.SWAP
        
        temp_spec = ModelSpec(
            name="temp", size_gb=size_gb, tier=tier_enum, 
            load_time_estimate=0, capabilities=[]
        )
        
        return self.is_model_safe_to_load(temp_spec)
    
    async def handle_request(self, request: Dict) -> Dict:
        """Enhanced request handler with hot loading support"""
        
        # Hot loading requests
        if "hot_load" in request:
            return await self._handle_hot_load(request["hot_load"])
        
        if "load_status" in request:
            return self._handle_load_status(request["load_status"])
        
        if "list_models" in request:
            return self._handle_list_models()
        
        # Standard Phase 2 requests
        return await self.process_request(request)
    
    async def _handle_hot_load(self, hot_load_request: Dict) -> Dict:
        """Handle hot loading request"""
        model_name = hot_load_request.get("model_name")
        model_config = hot_load_request.get("model_config")
        
        if not model_name or not model_config:
            return {"status": "error", "reason": "Missing model_name or model_config"}
        
        if model_name in self.model_library:
            return {"status": "error", "reason": f"Model '{model_name}' already exists"}
        
        job_id = await self.hot_loader.hot_load_model(model_name, model_config)
        
        return {
            "status": "hot_load_started",
            "job_id": job_id,
            "model_name": model_name,
            "estimated_time": f"{model_config.get('size_gb', 1.0) * 1.5:.1f}s"
        }
    
    def _handle_load_status(self, job_id: str) -> Dict:
        """Handle load status request"""
        status = self.hot_loader.get_load_status(job_id)
        if not status:
            return {"status": "error", "reason": "Job ID not found"}
        return status
    
    def _handle_list_models(self) -> Dict:
        """Handle list models request"""
        active_loads = len([j for j in self.hot_loader.load_jobs.values() 
                           if j.status == LoadStatus.LOADING])
        
        return {
            "status": "success",
            "models": {name: {
                "size_gb": spec.size_gb,
                "tier": spec.tier.value,
                "capabilities": spec.capabilities
            } for name, spec in self.model_library.items()},
            "total_models": len(self.model_library),
            "active_hot_loads": active_loads
        }

async def demo_integrated_system():
    """Demo complete system with hot loading"""
    server = Phase2HotLoadServer()
    
    print("🔥 Phase 2 + Hot Loading Integration Demo")
    print("=" * 50)
    
    # Test 1: List initial models
    print("📋 Initial system state:")
    result = await server.handle_request({"list_models": True})
    print(f"  Models: {result['total_models']}")
    print(f"  Active loads: {result['active_hot_loads']}")
    
    # Test 2: Regular Phase 2 operation
    print(f"\n🧠 Regular model selection:")
    result = await server.handle_request({"priority": "speed", "capabilities": ["text-generation"]})
    print(f"  Selected: {result['model']} ({result['selection_time_ms']:.1f}ms)")
    
    # Test 3: Hot load new model
    print(f"\n🚀 Hot loading new model:")
    hot_load_result = await server.handle_request({
        "hot_load": {
            "model_name": "custom-model-v1",
            "model_config": {
                "size_gb": 1.8,
                "tier": "ram",
                "capabilities": ["text-generation", "custom-task"]
            }
        }
    })
    print(f"  Status: {hot_load_result['status']}")
    print(f"  Job ID: {hot_load_result.get('job_id', 'N/A')}")
    
    # Test 4: Monitor loading
    if hot_load_result.get("job_id"):
        job_id = hot_load_result["job_id"]
        print(f"\n⏳ Monitoring load progress:")
        
        for i in range(4):
            await asyncio.sleep(0.5)
            status = await server.handle_request({"load_status": job_id})
            print(f"  {status['progress']*100:.0f}% - {status['status']}")
            if status['status'] in ['success', 'failed']:
                break
    
    # Test 5: Use hot-loaded model
    print(f"\n🎯 Using hot-loaded model:")
    result = await server.handle_request({"model": "custom-model-v1"})
    if result['status'] == 'success':
        print(f"  ✅ Successfully selected hot-loaded model")
        print(f"  Model: {result['model']} ({result['size_gb']}GB)")
    else:
        print(f"  ❌ Error: {result.get('reason', 'Unknown')}")
    
    # Test 6: Final system state
    print(f"\n📊 Final system state:")
    result = await server.handle_request({"list_models": True})
    print(f"  Total models: {result['total_models']}")
    print(f"  New models available for selection")

if __name__ == "__main__":
    asyncio.run(demo_integrated_system())
