#!/usr/bin/env python3
"""
Dynamic Model Tier Management
Allows moving models between RAM/Swap tiers and adjusting memory allocation
"""

import asyncio
import psutil
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TierOperation(Enum):
    PROMOTE = "promote"    # Move to faster tier (swap -> ram)
    DEMOTE = "demote"      # Move to slower tier (ram -> swap)
    OPTIMIZE = "optimize"  # Auto-optimize based on usage

@dataclass
class TierMoveJob:
    model_name: str
    source_tier: str
    target_tier: str
    operation: TierOperation
    progress: float
    start_time: float
    estimated_time: float
    status: str = "running"
    error: Optional[str] = None

class DynamicTierManager:
    def __init__(self, main_server):
        self.main_server = main_server
        self.tier_jobs = {}
        self.usage_stats = {}  # Track model usage for optimization
        self.tier_limits = {
            "ram_max_gb": 5.0,    # Configurable RAM limit
            "swap_max_gb": 10.0,  # Configurable swap limit
            "ram_reserved_gb": 1.0  # Always keep 1GB RAM free
        }
    
    def get_tier_status(self) -> Dict:
        """Get current tier utilization"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Calculate current usage by tier
        ram_models = [m for m in self.main_server.model_library.values() 
                     if hasattr(m, 'tier') and m.tier.value == 'ram']
        swap_models = [m for m in self.main_server.model_library.values() 
                      if hasattr(m, 'tier') and m.tier.value == 'swap']
        
        ram_used_gb = sum(m.size_gb for m in ram_models)
        swap_used_gb = sum(m.size_gb for m in swap_models)
        
        return {
            "ram": {
                "used_gb": ram_used_gb,
                "available_gb": memory.available / (1024**3),
                "limit_gb": self.tier_limits["ram_max_gb"],
                "utilization": ram_used_gb / self.tier_limits["ram_max_gb"],
                "models": len(ram_models)
            },
            "swap": {
                "used_gb": swap_used_gb,
                "available_gb": (swap.total - swap.used) / (1024**3),
                "limit_gb": self.tier_limits["swap_max_gb"],
                "utilization": swap_used_gb / self.tier_limits["swap_max_gb"],
                "models": len(swap_models)
            }
        }
    
    def can_move_to_tier(self, model_name: str, target_tier: str) -> Tuple[bool, str]:
        """Check if model can be moved to target tier"""
        if model_name not in self.main_server.model_library:
            return False, f"Model '{model_name}' not found"
        
        model = self.main_server.model_library[model_name]
        model_size = model.size_gb
        tier_status = self.get_tier_status()
        
        if target_tier == "ram":
            available = tier_status["ram"]["available_gb"] - self.tier_limits["ram_reserved_gb"]
            current_used = tier_status["ram"]["used_gb"]
            
            if current_used + model_size > self.tier_limits["ram_max_gb"]:
                return False, f"RAM limit exceeded: {current_used + model_size:.1f}GB > {self.tier_limits['ram_max_gb']}GB"
            
            if model_size > available:
                return False, f"Insufficient RAM: need {model_size}GB, have {available:.1f}GB"
            
            return True, "RAM promotion possible"
        
        elif target_tier == "swap":
            current_used = tier_status["swap"]["used_gb"]
            
            if current_used + model_size > self.tier_limits["swap_max_gb"]:
                return False, f"Swap limit exceeded: {current_used + model_size:.1f}GB > {self.tier_limits['swap_max_gb']}GB"
            
            return True, "Swap demotion possible"
        
        return False, f"Unknown target tier: {target_tier}"
    
    async def move_model_tier(self, model_name: str, target_tier: str, 
                             operation: TierOperation = TierOperation.PROMOTE) -> str:
        """Move model between tiers"""
        job_id = f"tier_{operation.value}_{model_name}_{int(time.time())}"
        
        model = self.main_server.model_library[model_name]
        source_tier = model.tier.value
        
        # Estimate time based on model size and operation
        if operation == TierOperation.PROMOTE:  # swap -> ram
            estimated_time = model.size_gb * 0.3  # 0.3s per GB
        else:  # ram -> swap
            estimated_time = model.size_gb * 0.2  # 0.2s per GB
        
        job = TierMoveJob(
            model_name=model_name,
            source_tier=source_tier,
            target_tier=target_tier,
            operation=operation,
            progress=0.0,
            start_time=time.time(),
            estimated_time=estimated_time
        )
        
        self.tier_jobs[job_id] = job
        
        # Start background tier move
        asyncio.create_task(self._execute_tier_move(job_id, job))
        
        return job_id
    
    async def _execute_tier_move(self, job_id: str, job: TierMoveJob):
        """Execute tier move operation"""
        try:
            model = self.main_server.model_library[job.model_name]
            
            # Step 1: Validate move
            job.progress = 0.1
            can_move, reason = self.can_move_to_tier(job.model_name, job.target_tier)
            if not can_move:
                raise RuntimeError(reason)
            
            # Step 2: Prepare target tier
            job.progress = 0.3
            await asyncio.sleep(0.2)  # Simulate preparation
            
            # Step 3: Move model data
            job.progress = 0.6
            await asyncio.sleep(job.estimated_time * 0.6)  # Main move operation
            
            # Step 4: Update model tier
            job.progress = 0.9
            from phase2_complete_integration import ModelTier
            new_tier = ModelTier.RAM if job.target_tier == "ram" else ModelTier.SWAP
            
            # Update load time estimate
            if new_tier == ModelTier.RAM:
                model.load_time_estimate = model.size_gb * 0.1
            else:
                model.load_time_estimate = model.size_gb * 0.5
            
            model.tier = new_tier
            
            # Step 5: Complete
            job.progress = 1.0
            job.status = "success"
            
            print(f"✅ Moved '{job.model_name}' from {job.source_tier} to {job.target_tier}")
            
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            print(f"❌ Failed to move '{job.model_name}': {e}")
    
    def update_tier_limits(self, new_limits: Dict) -> Dict:
        """Update tier allocation limits"""
        old_limits = self.tier_limits.copy()
        
        # Validate new limits
        if "ram_max_gb" in new_limits:
            if new_limits["ram_max_gb"] < 1.0:
                return {"status": "error", "reason": "RAM limit must be >= 1.0GB"}
            self.tier_limits["ram_max_gb"] = new_limits["ram_max_gb"]
        
        if "swap_max_gb" in new_limits:
            if new_limits["swap_max_gb"] < 2.0:
                return {"status": "error", "reason": "Swap limit must be >= 2.0GB"}
            self.tier_limits["swap_max_gb"] = new_limits["swap_max_gb"]
        
        if "ram_reserved_gb" in new_limits:
            if new_limits["ram_reserved_gb"] < 0.5:
                return {"status": "error", "reason": "RAM reserved must be >= 0.5GB"}
            self.tier_limits["ram_reserved_gb"] = new_limits["ram_reserved_gb"]
        
        return {
            "status": "success",
            "old_limits": old_limits,
            "new_limits": self.tier_limits.copy()
        }
    
    def get_tier_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of tier move job"""
        if job_id not in self.tier_jobs:
            return None
        
        job = self.tier_jobs[job_id]
        return {
            "job_id": job_id,
            "model_name": job.model_name,
            "operation": job.operation.value,
            "source_tier": job.source_tier,
            "target_tier": job.target_tier,
            "progress": job.progress,
            "status": job.status,
            "elapsed_time": time.time() - job.start_time,
            "estimated_time": job.estimated_time,
            "error": job.error
        }
    
    async def auto_optimize_tiers(self) -> List[str]:
        """Automatically optimize model placement based on usage"""
        tier_status = self.get_tier_status()
        optimizations = []
        
        # Find frequently used swap models that could be promoted
        swap_models = [m for m in self.main_server.model_library.values() 
                      if hasattr(m, 'tier') and m.tier.value == 'swap']
        
        for model in swap_models:
            usage_count = self.usage_stats.get(model.name, 0)
            if usage_count > 5:  # Frequently used threshold
                can_promote, _ = self.can_move_to_tier(model.name, "ram")
                if can_promote:
                    job_id = await self.move_model_tier(model.name, "ram", TierOperation.OPTIMIZE)
                    optimizations.append(f"Promoting {model.name} to RAM (usage: {usage_count})")
        
        return optimizations

class TierManagedServer:
    """Server with dynamic tier management"""
    
    def __init__(self):
        # Import from previous systems
        from phase2_with_hot_loading import Phase2HotLoadServer
        self.base_server = Phase2HotLoadServer()
        self.tier_manager = DynamicTierManager(self.base_server)
    
    async def handle_request(self, request: Dict) -> Dict:
        """Enhanced request handler with tier management"""
        
        # Tier management requests
        if "tier_status" in request:
            return {"status": "success", "tiers": self.tier_manager.get_tier_status()}
        
        if "move_tier" in request:
            return await self._handle_tier_move(request["move_tier"])
        
        if "tier_job_status" in request:
            return self._handle_tier_job_status(request["tier_job_status"])
        
        if "update_limits" in request:
            return self.tier_manager.update_tier_limits(request["update_limits"])
        
        if "auto_optimize" in request:
            optimizations = await self.tier_manager.auto_optimize_tiers()
            return {"status": "success", "optimizations": optimizations}
        
        # Track usage for optimization
        if "model" in request:
            model_name = request["model"]
            self.tier_manager.usage_stats[model_name] = self.tier_manager.usage_stats.get(model_name, 0) + 1
        
        # Delegate to base server
        return await self.base_server.handle_request(request)
    
    async def _handle_tier_move(self, move_request: Dict) -> Dict:
        """Handle tier move request"""
        model_name = move_request.get("model_name")
        target_tier = move_request.get("target_tier")
        
        if not model_name or not target_tier:
            return {"status": "error", "reason": "Missing model_name or target_tier"}
        
        # Determine operation type
        if model_name not in self.base_server.model_library:
            return {"status": "error", "reason": f"Model '{model_name}' not found"}
        
        current_tier = self.base_server.model_library[model_name].tier.value
        if current_tier == target_tier:
            return {"status": "error", "reason": f"Model already in {target_tier} tier"}
        
        operation = TierOperation.PROMOTE if target_tier == "ram" else TierOperation.DEMOTE
        
        # Check if move is possible
        can_move, reason = self.tier_manager.can_move_to_tier(model_name, target_tier)
        if not can_move:
            return {"status": "error", "reason": reason}
        
        # Start tier move
        job_id = await self.tier_manager.move_model_tier(model_name, target_tier, operation)
        
        return {
            "status": "tier_move_started",
            "job_id": job_id,
            "model_name": model_name,
            "operation": operation.value,
            "source_tier": current_tier,
            "target_tier": target_tier
        }
    
    def _handle_tier_job_status(self, job_id: str) -> Dict:
        """Handle tier job status request"""
        status = self.tier_manager.get_tier_job_status(job_id)
        if not status:
            return {"status": "error", "reason": "Job ID not found"}
        return status

async def demo_tier_management():
    """Demonstrate dynamic tier management"""
    server = TierManagedServer()
    
    print("🎯 Dynamic Tier Management Demo")
    print("=" * 50)
    
    # Show initial tier status
    result = await server.handle_request({"tier_status": True})
    print("📊 Initial Tier Status:")
    for tier, info in result["tiers"].items():
        print(f"  {tier.upper()}: {info['used_gb']:.1f}GB used, {info['models']} models")
    
    # Move a model from swap to RAM
    print(f"\n🚀 Moving llama-7b from swap to RAM:")
    move_result = await server.handle_request({
        "move_tier": {
            "model_name": "llama-7b",
            "target_tier": "ram"
        }
    })
    print(f"  Status: {move_result['status']}")
    
    if move_result.get("job_id"):
        job_id = move_result["job_id"]
        # Monitor progress
        for i in range(4):
            await asyncio.sleep(0.5)
            status = await server.handle_request({"tier_job_status": job_id})
            print(f"  Progress: {status['progress']*100:.0f}% - {status['status']}")
            if status['status'] in ['success', 'failed']:
                break
    
    # Show updated tier status
    result = await server.handle_request({"tier_status": True})
    print(f"\n📊 Updated Tier Status:")
    for tier, info in result["tiers"].items():
        print(f"  {tier.upper()}: {info['used_gb']:.1f}GB used, {info['models']} models")
    
    # Test model selection with new tier
    print(f"\n🧠 Testing model selection:")
    result = await server.handle_request({"model": "llama-7b"})
    if result['status'] == 'success':
        print(f"  ✅ llama-7b now loads in {result.get('load_time', 'N/A')}s (was 3.5s)")
    
    # Adjust tier limits
    print(f"\n⚙️  Adjusting tier limits:")
    limit_result = await server.handle_request({
        "update_limits": {
            "ram_max_gb": 6.0,
            "swap_max_gb": 8.0
        }
    })
    print(f"  Status: {limit_result['status']}")
    if limit_result['status'] == 'success':
        print(f"  New RAM limit: {limit_result['new_limits']['ram_max_gb']}GB")

if __name__ == "__main__":
    asyncio.run(demo_tier_management())
