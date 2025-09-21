#!/usr/bin/env python3
"""
PHASE 2 INTEGRATION: Enhanced Model Selection + Phase 1 Production Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import psutil
import gc
from typing import List, Optional, Dict, Any
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced Request Models
class EnhancedInferenceRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 20
    temperature: Optional[float] = 0.7
    
    # NEW: Model selection options
    model: Optional[str] = None              # Manual selection
    auto_select: Optional[bool] = None       # Auto selection
    preferred_model: Optional[str] = None    # Hybrid mode

class BatchRequest(BaseModel):
    prompts: List[str]
    max_length: Optional[int] = 20
    model: Optional[str] = None
    auto_select: Optional[bool] = None

class ModelLoadRequest(BaseModel):
    model_name: str
    priority: Optional[str] = "normal"

# Enhanced Model Selector
class EnhancedModelSelector:
    def __init__(self, models_dict: Dict[str, Any]):
        self.models = models_dict
        self.selection_stats = {"manual": 0, "auto": 0, "hybrid": 0}
        
    async def select_model(self, request: EnhancedInferenceRequest) -> tuple:
        start_time = time.time()
        
        if not self.models:
            raise HTTPException(400, "No models loaded. Load a model first.")
        
        # Selection Logic
        if request.model:
            # Manual Selection
            if request.model not in self.models:
                available = list(self.models.keys())
                raise HTTPException(404, f"Model '{request.model}' not available. Available: {available}")
            
            selected = request.model
            mode = "manual"
            reasoning = f"User specified model: {request.model}"
            self.selection_stats["manual"] += 1
            
        elif request.preferred_model:
            # Hybrid Selection
            if request.preferred_model in self.models:
                selected = request.preferred_model
                mode = "hybrid_preferred"
                reasoning = f"Used preferred model: {request.preferred_model}"
            else:
                selected = list(self.models.keys())[0]
                mode = "hybrid_fallback"
                reasoning = f"Preferred '{request.preferred_model}' unavailable, used auto selection"
            self.selection_stats["hybrid"] += 1
            
        else:
            # Auto Selection (default - Phase 1 compatible)
            selected = list(self.models.keys())[0]
            mode = "auto"
            reasoning = "Auto-selected first available model (Phase 1 compatible)"
            self.selection_stats["auto"] += 1
        
        selection_time_ms = (time.time() - start_time) * 1000
        return selected, mode, reasoning, selection_time_ms

# Integrated AI Server
class IntegratedAIServer:
    def __init__(self):
        self.app = FastAPI(title="Enhanced Jetson AI Server - Phase 2", version="2.0.0")
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Phase 1 components
        self.models = {}
        self.model_stats = {}
        self.system_stats = {"requests": 0, "start_time": time.time()}
        
        # Phase 2 components
        self.model_selector = EnhancedModelSelector(self.models)
        
        self.setup_routes()
    
    def get_system_metrics(self):
        memory = psutil.virtual_memory()
        return {
            "ram_used_gb": memory.used / 1024**3,
            "ram_total_gb": memory.total / 1024**3,
            "ram_percent": memory.percent,
            "cpu_percent": psutil.cpu_percent(),
            "gpu_memory_gb": torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0,
            "active_models": len(self.models),
            "uptime": time.time() - self.system_stats["start_time"]
        }
    
    def setup_routes(self):
        @self.app.get("/health")
        def health():
            return {
                "status": "healthy", 
                "timestamp": time.time(), 
                "version": "2.0.0",
                "phase": "2_integrated"
            }

        @self.app.get("/status")
        def status():
            metrics = self.get_system_metrics()
            return {
                "active_models": list(self.models.keys()),
                "memory_usage_gb": metrics["ram_used_gb"],
                "memory_budget_gb": metrics["ram_total_gb"],
                "cpu_percent": metrics["cpu_percent"],
                "gpu_memory_gb": metrics["gpu_memory_gb"],
                "queue_size": 0,
                "uptime": metrics["uptime"],
                "total_requests": self.system_stats["requests"],
                "selection_stats": self.model_selector.selection_stats
            }

        @self.app.get("/models")
        def get_models():
            model_info = {}
            for name, data in self.models.items():
                model_info[name] = {
                    "load_time": data.get("load_time", 0),
                    "usage_count": self.model_stats.get(name, {}).get("usage_count", 0),
                    "last_used": self.model_stats.get(name, {}).get("last_used", 0),
                    "priority": data.get("priority", "normal")
                }
            
            return {
                "active_models": model_info,
                "available_models": ["distilgpt2", "gpt2", "microsoft/DialoGPT-small"],
                "selection_modes": ["manual", "auto", "hybrid"],
                "selection_stats": self.model_selector.selection_stats
            }

        @self.app.post("/load_model")
        def load_model(request: ModelLoadRequest):
            try:
                if request.model_name in self.models:
                    return {"message": f"Model {request.model_name} already loaded"}
                
                logger.info(f"Loading model: {request.model_name}")
                start_time = time.time()
                
                tokenizer = AutoTokenizer.from_pretrained(request.model_name)
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                    
                model = AutoModelForCausalLM.from_pretrained(request.model_name)
                
                load_time = time.time() - start_time
                
                self.models[request.model_name] = {
                    "model": model,
                    "tokenizer": tokenizer,
                    "load_time": load_time,
                    "priority": request.priority
                }
                
                self.model_stats[request.model_name] = {
                    "usage_count": 0,
                    "last_used": time.time()
                }
                
                self.model_selector.models = self.models
                
                return {
                    "message": f"Model {request.model_name} loaded successfully",
                    "load_time": load_time
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/inference")
        async def enhanced_inference(request: EnhancedInferenceRequest):
            try:
                self.system_stats["requests"] += 1
                total_start = time.time()
                
                # Phase 2: Enhanced Model Selection
                selected_model, selection_mode, reasoning, selection_time_ms = await self.model_selector.select_model(request)
                
                # Phase 1: Execute Inference
                model_data = self.models[selected_model]
                model = model_data["model"]
                tokenizer = model_data["tokenizer"]
                
                # Update stats
                if selected_model not in self.model_stats:
                    self.model_stats[selected_model] = {"usage_count": 0, "last_used": 0}
                
                self.model_stats[selected_model]["usage_count"] += 1
                self.model_stats[selected_model]["last_used"] = time.time()
                
                # Tokenize and generate
                inputs = tokenizer.encode(request.prompt, return_tensors="pt")
                
                inference_start = time.time()
                with torch.no_grad():
                    outputs = model.generate(
                        inputs,
                        max_length=inputs.shape[1] + request.max_length,
                        do_sample=True,
                        temperature=request.temperature,
                        pad_token_id=tokenizer.eos_token_id
                    )
                
                inference_time = time.time() - inference_start
                result = tokenizer.decode(outputs[0], skip_special_tokens=True)
                tokens_generated = len(outputs[0]) - len(inputs[0])
                
                total_time = time.time() - total_start
                
                return {
                    # Phase 1 response format (backward compatible)
                    "response": result,
                    "model_used": selected_model,
                    "inference_time": inference_time,
                    "tokens_generated": tokens_generated,
                    "tokens_per_second": tokens_generated / inference_time if inference_time > 0 else 0,
                    "timestamp": time.time(),
                    
                    # NEW: Phase 2 selection information
                    "selection_info": {
                        "selection_mode": selection_mode,
                        "selection_time_ms": selection_time_ms,
                        "reasoning": reasoning
                    },
                    "total_time": total_time
                }
                
            except Exception as e:
                logger.error(f"Enhanced inference failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/batch_inference")
        async def enhanced_batch_inference(request: BatchRequest):
            try:
                if not self.models:
                    raise HTTPException(status_code=400, detail="No models loaded")
                
                results = []
                start_time = time.time()
                
                for prompt in request.prompts:
                    inference_req = EnhancedInferenceRequest(
                        prompt=prompt, 
                        max_length=request.max_length,
                        model=request.model,
                        auto_select=request.auto_select
                    )
                    result = await enhanced_inference(inference_req)
                    results.append(result)
                
                total_time = time.time() - start_time
                
                return {
                    "results": results,
                    "batch_size": len(request.prompts),
                    "total_time": total_time,
                    "avg_time_per_request": total_time / len(request.prompts)
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/performance")
        def performance():
            metrics = self.get_system_metrics()
            
            model_performance = {}
            for name, stats in self.model_stats.items():
                model_performance[name] = {
                    "usage_count": stats["usage_count"],
                    "last_used": stats["last_used"],
                    "efficiency": stats["usage_count"] / max(1, (time.time() - stats["last_used"]) / 3600)
                }
            
            return {
                "system_metrics": metrics,
                "model_performance": model_performance,
                "selection_analytics": {
                    "selection_stats": self.model_selector.selection_stats,
                    "total_selections": sum(self.model_selector.selection_stats.values())
                },
                "recommendations": [
                    "System running optimally" if metrics["ram_percent"] < 80 else "Consider memory optimization",
                    f"Processed {self.system_stats['requests']} requests since startup"
                ]
            }

        @self.app.post("/optimize")
        def optimize():
            try:
                memory = psutil.virtual_memory()
                if memory.percent > 85:
                    if len(self.models) > 1:
                        least_used = min(self.model_stats.items(), key=lambda x: x[1]["usage_count"])
                        model_name = least_used[0]
                        
                        del self.models[model_name]
                        self.model_selector.models = self.models
                        gc.collect()
                        
                        return {"message": f"Optimized: Removed {model_name} to free memory"}
                
                return {"message": "System already optimized"}
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 STARTING INTEGRATED PHASE 2 SERVER")
    print("📡 Enhanced endpoints:")
    print("   POST /inference - Now supports model selection")
    print("   POST /batch_inference - Enhanced with selection")
    print("   GET /models - Shows selection capabilities")
    print("   GET /performance - Includes selection analytics")
    print("\n🌐 Server starting on http://localhost:8000")
    
    server = IntegratedAIServer()
    uvicorn.run(server.app, host="0.0.0.0", port=8000)
