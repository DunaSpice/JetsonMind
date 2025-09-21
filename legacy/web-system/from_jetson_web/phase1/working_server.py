#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import psutil
import gc
from typing import List, Optional
import asyncio
import threading

app = FastAPI(title="Enhanced Jetson AI Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
models = {}
model_stats = {}
system_stats = {"requests": 0, "start_time": time.time()}

class InferenceRequest(BaseModel):
    prompt: str
    max_length: Optional[int] = 20
    temperature: Optional[float] = 0.7

class BatchRequest(BaseModel):
    prompts: List[str]
    max_length: Optional[int] = 20

class ModelLoadRequest(BaseModel):
    model_name: str
    priority: Optional[str] = "normal"

def get_system_metrics():
    memory = psutil.virtual_memory()
    return {
        "ram_used_gb": memory.used / 1024**3,
        "ram_total_gb": memory.total / 1024**3,
        "ram_percent": memory.percent,
        "cpu_percent": psutil.cpu_percent(),
        "gpu_memory_gb": torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0,
        "active_models": len(models),
        "uptime": time.time() - system_stats["start_time"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": time.time(), "version": "2.0.0"}

@app.get("/status")
def status():
    metrics = get_system_metrics()
    return {
        "active_models": list(models.keys()),
        "memory_usage_gb": metrics["ram_used_gb"],
        "memory_budget_gb": metrics["ram_total_gb"],
        "cpu_percent": metrics["cpu_percent"],
        "gpu_memory_gb": metrics["gpu_memory_gb"],
        "queue_size": 0,
        "uptime": metrics["uptime"],
        "total_requests": system_stats["requests"]
    }

@app.get("/models")
def get_models():
    model_info = {}
    for name, data in models.items():
        model_info[name] = {
            "load_time": data.get("load_time", 0),
            "usage_count": model_stats.get(name, {}).get("usage_count", 0),
            "last_used": model_stats.get(name, {}).get("last_used", 0)
        }
    
    return {
        "active_models": model_info,
        "available_models": ["distilgpt2", "gpt2", "microsoft/DialoGPT-small"]
    }

@app.post("/load_model")
def load_model(request: ModelLoadRequest):
    try:
        if request.model_name in models:
            return {"message": f"Model {request.model_name} already loaded"}
        
        print(f"Loading model: {request.model_name}")
        start_time = time.time()
        
        tokenizer = AutoTokenizer.from_pretrained(request.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(request.model_name)
        
        load_time = time.time() - start_time
        
        models[request.model_name] = {
            "model": model,
            "tokenizer": tokenizer,
            "load_time": load_time,
            "priority": request.priority
        }
        
        model_stats[request.model_name] = {
            "usage_count": 0,
            "last_used": time.time()
        }
        
        return {
            "message": f"Model {request.model_name} loaded successfully",
            "load_time": load_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inference")
def inference(request: InferenceRequest):
    try:
        system_stats["requests"] += 1
        
        if not models:
            raise HTTPException(status_code=400, detail="No models loaded. Load a model first.")
        
        # Use first available model
        model_name = list(models.keys())[0]
        model_data = models[model_name]
        
        model = model_data["model"]
        tokenizer = model_data["tokenizer"]
        
        # Update stats
        if model_name not in model_stats:
            model_stats[model_name] = {"usage_count": 0, "last_used": 0}
        
        model_stats[model_name]["usage_count"] += 1
        model_stats[model_name]["last_used"] = time.time()
        
        # Tokenize
        inputs = tokenizer.encode(request.prompt, return_tensors="pt")
        
        # Generate
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + request.max_length,
                do_sample=True,
                temperature=request.temperature,
                pad_token_id=tokenizer.eos_token_id
            )
        
        inference_time = time.time() - start_time
        
        # Decode
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        tokens_generated = len(outputs[0]) - len(inputs[0])
        
        return {
            "response": result,
            "model_used": model_name,
            "inference_time": inference_time,
            "tokens_generated": tokens_generated,
            "tokens_per_second": tokens_generated / inference_time if inference_time > 0 else 0,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_inference")
def batch_inference(request: BatchRequest):
    try:
        if not models:
            raise HTTPException(status_code=400, detail="No models loaded")
        
        results = []
        start_time = time.time()
        
        for prompt in request.prompts:
            inference_req = InferenceRequest(prompt=prompt, max_length=request.max_length)
            result = inference(inference_req)
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

@app.get("/performance")
def performance():
    metrics = get_system_metrics()
    
    model_performance = {}
    for name, stats in model_stats.items():
        model_performance[name] = {
            "usage_count": stats["usage_count"],
            "last_used": stats["last_used"],
            "efficiency": stats["usage_count"] / max(1, (time.time() - stats["last_used"]) / 3600)
        }
    
    return {
        "system_metrics": metrics,
        "model_performance": model_performance,
        "recommendations": [
            "System running optimally" if metrics["ram_percent"] < 80 else "Consider memory optimization",
            f"Processed {system_stats['requests']} requests since startup"
        ]
    }

@app.post("/optimize")
def optimize():
    try:
        # Simple optimization: clear unused models if memory > 85%
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            # Find least used model
            if len(models) > 1:
                least_used = min(model_stats.items(), key=lambda x: x[1]["usage_count"])
                model_name = least_used[0]
                
                del models[model_name]
                gc.collect()
                
                return {"message": f"Optimized: Removed {model_name} to free memory"}
        
        return {"message": "System already optimized"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced Jetson AI Server...")
    print("📡 Endpoints: /health, /status, /models, /load_model, /inference, /batch_inference")
    print("🌐 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
