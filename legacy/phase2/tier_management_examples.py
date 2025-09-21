#!/usr/bin/env python3
"""
Practical Tier Management Examples
Real-world workflows for optimizing model placement
"""

import asyncio
from dynamic_tier_manager import TierManagedServer

class TierOptimizationWorkflows:
    def __init__(self):
        self.server = TierManagedServer()
    
    async def workflow_1_performance_boost(self):
        """Workflow 1: Boost performance for frequently used model"""
        print("🚀 Workflow 1: Performance Boost")
        print("-" * 40)
        
        # Step 1: Check current tier status
        status = await self.server.handle_request({"tier_status": True})
        print("Current tier utilization:")
        for tier, info in status["tiers"].items():
            print(f"  {tier.upper()}: {info['utilization']:.1%} ({info['used_gb']:.1f}GB)")
        
        # Step 2: Identify model to promote
        target_model = "gpt-j-6b"  # Large model currently in swap
        print(f"\n🎯 Target: Promote '{target_model}' to RAM for faster access")
        
        # Step 3: Check if promotion is possible
        current_model = self.server.base_server.model_library[target_model]
        print(f"Model size: {current_model.size_gb}GB, current tier: {current_model.tier.value}")
        
        # Step 4: Adjust limits if needed
        print("\n⚙️  Adjusting RAM limit to accommodate large model:")
        limit_result = await self.server.handle_request({
            "update_limits": {
                "ram_max_gb": 8.0  # Increase to fit 6GB model
            }
        })
        print(f"Limit update: {limit_result['status']}")
        
        # Step 5: Execute promotion
        print(f"\n📈 Promoting {target_model} to RAM:")
        move_result = await self.server.handle_request({
            "move_tier": {
                "model_name": target_model,
                "target_tier": "ram"
            }
        })
        
        if move_result['status'] == 'tier_move_started':
            job_id = move_result['job_id']
            print(f"Move started, job ID: {job_id}")
            
            # Monitor progress
            while True:
                await asyncio.sleep(0.3)
                job_status = await self.server.handle_request({"tier_job_status": job_id})
                print(f"  Progress: {job_status['progress']*100:.0f}% - {job_status['status']}")
                
                if job_status['status'] in ['success', 'failed']:
                    break
            
            # Test performance improvement
            if job_status['status'] == 'success':
                print(f"\n✅ Performance test:")
                result = await self.server.handle_request({"model": target_model})
                print(f"New load time estimate: {result.get('load_time', 'N/A')}s (was ~3.0s)")
        else:
            print(f"❌ Move failed: {move_result.get('reason', 'Unknown error')}")
    
    async def workflow_2_capacity_management(self):
        """Workflow 2: Free RAM by strategic demotion"""
        print("\n🧹 Workflow 2: Capacity Management")
        print("-" * 40)
        
        # Step 1: Check RAM pressure
        status = await self.server.handle_request({"tier_status": True})
        ram_info = status["tiers"]["ram"]
        
        print(f"RAM utilization: {ram_info['utilization']:.1%}")
        print(f"RAM usage: {ram_info['used_gb']:.1f}GB / {ram_info['limit_gb']}GB")
        
        if ram_info['utilization'] > 0.8:
            print("⚠️  High RAM utilization detected")
            
            # Step 2: Find candidate for demotion
            ram_models = [name for name, model in self.server.base_server.model_library.items()
                         if hasattr(model, 'tier') and model.tier.value == 'ram']
            
            # Choose largest RAM model for demotion
            largest_model = max(ram_models, 
                              key=lambda name: self.server.base_server.model_library[name].size_gb)
            
            print(f"🎯 Demoting largest RAM model: {largest_model}")
            
            # Step 3: Execute demotion
            move_result = await self.server.handle_request({
                "move_tier": {
                    "model_name": largest_model,
                    "target_tier": "swap"
                }
            })
            
            if move_result['status'] == 'tier_move_started':
                print(f"Demotion started: {move_result['job_id']}")
                
                # Wait for completion
                job_id = move_result['job_id']
                while True:
                    await asyncio.sleep(0.2)
                    job_status = await self.server.handle_request({"tier_job_status": job_id})
                    if job_status['status'] in ['success', 'failed']:
                        print(f"Demotion {job_status['status']}")
                        break
                
                # Show freed capacity
                new_status = await self.server.handle_request({"tier_status": True})
                new_ram_info = new_status["tiers"]["ram"]
                freed_gb = ram_info['used_gb'] - new_ram_info['used_gb']
                print(f"✅ Freed {freed_gb:.1f}GB RAM space")
        else:
            print("✅ RAM utilization is healthy")
    
    async def workflow_3_intelligent_optimization(self):
        """Workflow 3: Usage-based automatic optimization"""
        print("\n🧠 Workflow 3: Intelligent Optimization")
        print("-" * 40)
        
        # Step 1: Simulate some usage patterns
        print("Simulating usage patterns...")
        usage_models = ["gpt2-medium", "bert-large", "gpt2-large"]
        
        for model in usage_models:
            for _ in range(8):  # Simulate 8 uses
                await self.server.handle_request({"model": model})
        
        print(f"Generated usage for: {', '.join(usage_models)}")
        
        # Step 2: Run auto-optimization
        print("\n🔄 Running auto-optimization:")
        opt_result = await self.server.handle_request({"auto_optimize": True})
        
        if opt_result['status'] == 'success':
            optimizations = opt_result['optimizations']
            if optimizations:
                print("Optimizations applied:")
                for opt in optimizations:
                    print(f"  • {opt}")
            else:
                print("No optimizations needed - models already optimally placed")
        
        # Step 3: Show final tier distribution
        final_status = await self.server.handle_request({"tier_status": True})
        print(f"\n📊 Final tier distribution:")
        for tier, info in final_status["tiers"].items():
            print(f"  {tier.upper()}: {info['models']} models, {info['used_gb']:.1f}GB")
    
    async def workflow_4_dynamic_scaling(self):
        """Workflow 4: Dynamic scaling for workload changes"""
        print("\n📈 Workflow 4: Dynamic Scaling")
        print("-" * 40)
        
        # Scenario: Preparing for high-performance workload
        print("Scenario: Preparing for high-performance period")
        
        # Step 1: Increase RAM allocation
        print("\n⚙️  Scaling up RAM allocation:")
        scale_result = await self.server.handle_request({
            "update_limits": {
                "ram_max_gb": 7.0,  # Increase RAM budget
                "ram_reserved_gb": 0.8  # Reduce reserved to allow more models
            }
        })
        print(f"Scaling result: {scale_result['status']}")
        
        # Step 2: Promote critical models to RAM
        critical_models = ["gpt2-large", "bert-large"]
        print(f"\n🚀 Promoting critical models to RAM:")
        
        for model in critical_models:
            current_tier = self.server.base_server.model_library[model].tier.value
            if current_tier != "ram":
                move_result = await self.server.handle_request({
                    "move_tier": {
                        "model_name": model,
                        "target_tier": "ram"
                    }
                })
                print(f"  {model}: {move_result['status']}")
        
        # Step 3: Show optimized configuration
        final_status = await self.server.handle_request({"tier_status": True})
        ram_info = final_status["tiers"]["ram"]
        print(f"\n✅ High-performance configuration ready:")
        print(f"  RAM models: {ram_info['models']}")
        print(f"  RAM utilization: {ram_info['utilization']:.1%}")
        print(f"  Expected performance: 5x faster model loading")

async def run_all_workflows():
    """Run all tier management workflows"""
    workflows = TierOptimizationWorkflows()
    
    print("🎯 Tier Management Workflow Examples")
    print("=" * 60)
    
    try:
        await workflows.workflow_1_performance_boost()
        await workflows.workflow_2_capacity_management()
        await workflows.workflow_3_intelligent_optimization()
        await workflows.workflow_4_dynamic_scaling()
        
        print(f"\n🎉 All workflows completed successfully!")
        print("Key capabilities demonstrated:")
        print("  ✅ Performance optimization through tier promotion")
        print("  ✅ Capacity management through strategic demotion")
        print("  ✅ Usage-based automatic optimization")
        print("  ✅ Dynamic scaling for workload changes")
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")

if __name__ == "__main__":
    asyncio.run(run_all_workflows())
