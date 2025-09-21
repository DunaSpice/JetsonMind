#!/usr/bin/env python3
"""
Hot Model Loading System
Allows loading new models into running system without interruption
"""

import asyncio
import time
import threading
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

class LoadStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class LoadJob:
    model_name: str
    model_config: Dict
    status: LoadStatus
    progress: float
    start_time: float
    error_message: Optional[str] = None

class HotModelLoader:
    def __init__(self, main_server):
        self.main_server = main_server
        self.load_jobs = {}
        self.background_tasks = set()
        
    async def hot_load_model(self, model_name: str, model_config: Dict) -> str:
        """Load new model while system is running"""
        job_id = f"load_{model_name}_{int(time.time())}"
        
        # Create load job
        job = LoadJob(
            model_name=model_name,
            model_config=model_config,
            status=LoadStatus.LOADING,
            progress=0.0,
            start_time=time.time()
        )
        self.load_jobs[job_id] = job
        
        # Start background loading
        task = asyncio.create_task(self._background_load(job_id, job))
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        
        return job_id
    
    async def _background_load(self, job_id: str, job: LoadJob):
        """Background model loading process"""
        try:
            # Step 1: Validate model config
            job.progress = 0.1
            if not self._validate_model_config(job.model_config):
                raise ValueError("Invalid model configuration")
            
            # Step 2: Check system capacity
            job.progress = 0.2
            safe, reason = self.main_server.is_model_safe_to_load_from_config(job.model_config)
            if not safe:
                raise RuntimeError(f"Unsafe to load: {reason}")
            
            # Step 3: Download/prepare model (simulated)
            job.progress = 0.4
            await asyncio.sleep(1.0)  # Simulate download
            
            # Step 4: Load model into memory
            job.progress = 0.7
            await asyncio.sleep(0.5)  # Simulate loading
            
            # Step 5: Register with main server
            job.progress = 0.9
            self.main_server.register_hot_loaded_model(job.model_name, job.model_config)
            
            # Complete
            job.status = LoadStatus.SUCCESS
            job.progress = 1.0
            
        except Exception as e:
            job.status = LoadStatus.FAILED
            job.error_message = str(e)
    
    def _validate_model_config(self, config: Dict) -> bool:
        """Validate model configuration"""
        required_fields = ["size_gb", "capabilities", "tier"]
        return all(field in config for field in required_fields)
    
    def get_load_status(self, job_id: str) -> Optional[Dict]:
        """Get status of loading job"""
        if job_id not in self.load_jobs:
            return None
            
        job = self.load_jobs[job_id]
        return {
            "job_id": job_id,
            "model_name": job.model_name,
            "status": job.status.value,
            "progress": job.progress,
            "elapsed_time": time.time() - job.start_time,
            "error": job.error_message
        }
    
    def list_active_loads(self) -> List[Dict]:
        """List all active loading jobs"""
        return [self.get_load_status(job_id) for job_id in self.load_jobs.keys()]

class HotLoadableServer:
    """Enhanced server with hot loading capability"""
    
    def __init__(self):
        # Import existing model library from Phase 2
        self.model_library = {
            "gpt2-small": {"size_gb": 0.5, "tier": "ram", "capabilities": ["text-generation"]},
            "gpt2-medium": {"size_gb": 1.5, "tier": "ram", "capabilities": ["text-generation"]},
            "gpt2-large": {"size_gb": 3.0, "tier": "ram", "capabilities": ["text-generation"]},
            "bert-large": {"size_gb": 1.3, "tier": "ram", "capabilities": ["text-classification"]},
            "gpt-j-6b": {"size_gb": 6.0, "tier": "swap", "capabilities": ["text-generation"]},
            "llama-7b": {"size_gb": 7.0, "tier": "swap", "capabilities": ["text-generation"]},
        }
        
        self.hot_loader = HotModelLoader(self)
        self.current_model = None
    
    def is_model_safe_to_load_from_config(self, config: Dict) -> tuple:
        """Check if model config is safe to load"""
        size_gb = config.get("size_gb", 0)
        tier = config.get("tier", "storage")
        
        if tier == "storage" or size_gb > 10.5:
            return False, f"Model too large: {size_gb}GB"
        
        # Use existing safety logic from Phase 2
        import psutil
        memory = psutil.virtual_memory()
        ram_available = memory.available / (1024**3)
        
        if tier == "ram" and size_gb <= ram_available * 0.7:
            return True, "Safe for RAM loading"
        elif tier == "swap" and size_gb <= 15.0:  # Conservative swap limit
            return True, "Safe for swap loading"
        
        return False, "Insufficient system resources"
    
    def register_hot_loaded_model(self, model_name: str, config: Dict):
        """Register newly loaded model"""
        self.model_library[model_name] = config
        print(f"✅ Hot loaded model '{model_name}' registered")
    
    async def handle_hot_load_request(self, request: Dict) -> Dict:
        """Handle hot loading API request"""
        model_name = request.get("model_name")
        model_config = request.get("model_config")
        
        if not model_name or not model_config:
            return {"status": "error", "reason": "Missing model_name or model_config"}
        
        if model_name in self.model_library:
            return {"status": "error", "reason": f"Model '{model_name}' already exists"}
        
        # Start hot loading
        job_id = await self.hot_loader.hot_load_model(model_name, model_config)
        
        return {
            "status": "loading_started",
            "job_id": job_id,
            "model_name": model_name,
            "message": "Hot loading started in background"
        }
    
    def handle_load_status_request(self, job_id: str) -> Dict:
        """Check status of hot loading job"""
        status = self.hot_loader.get_load_status(job_id)
        if not status:
            return {"status": "error", "reason": "Job ID not found"}
        return status
    
    def list_models(self) -> Dict:
        """List all available models including hot-loaded ones"""
        return {
            "models": list(self.model_library.keys()),
            "total_count": len(self.model_library),
            "active_loads": len([j for j in self.hot_loader.load_jobs.values() if j.status == LoadStatus.LOADING])
        }

async def demo_hot_loading():
    """Demonstrate hot loading capability"""
    server = HotLoadableServer()
    
    print("🔥 Hot Model Loading Demo")
    print("=" * 40)
    
    # Show initial models
    initial_models = server.list_models()
    print(f"Initial models: {initial_models['total_count']}")
    print(f"Models: {', '.join(initial_models['models'])}")
    
    # Hot load a new model
    print(f"\n🚀 Hot loading new model...")
    new_model_config = {
        "size_gb": 2.0,
        "tier": "ram", 
        "capabilities": ["text-generation", "chat"]
    }
    
    load_result = await server.handle_hot_load_request({
        "model_name": "chatgpt-mini",
        "model_config": new_model_config
    })
    
    print(f"Load started: {load_result}")
    job_id = load_result.get("job_id")
    
    # Monitor loading progress
    if job_id:
        for i in range(5):
            await asyncio.sleep(0.5)
            status = server.handle_load_status_request(job_id)
            print(f"Progress: {status['progress']*100:.0f}% - {status['status']}")
            
            if status['status'] in ['success', 'failed']:
                break
    
    # Show final models
    final_models = server.list_models()
    print(f"\n✅ Final models: {final_models['total_count']}")
    print(f"Models: {', '.join(final_models['models'])}")
    print(f"Hot loading successful: {'chatgpt-mini' in final_models['models']}")

if __name__ == "__main__":
    asyncio.run(demo_hot_loading())
