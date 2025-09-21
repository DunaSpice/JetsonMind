#!/usr/bin/env python3
"""
Phase 3: REST API Server
FastAPI server with OpenAPI documentation and user-friendly endpoints
"""

import asyncio
import sys
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import Phase 3 components
sys.path.append('/home/petr/phase3/schemas')
sys.path.append('/home/petr/phase3/inference')
sys.path.append('/home/petr/phase2')

from openapi_schema import *
from inference_engine import InferenceEngine, InferenceHelpers, InferenceConfig
from dynamic_tier_manager import TierManagedServer

# Initialize FastAPI app
app = FastAPI(
    title="Phase 3 Model Management & Inference API",
    description="Advanced model management with dynamic optimization and inference capabilities",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
model_manager = None
inference_engine = None
inference_helpers = None

@app.on_event("startup")
async def startup_event():
    """Initialize system components"""
    global model_manager, inference_engine, inference_helpers
    
    model_manager = TierManagedServer()
    inference_engine = InferenceEngine(model_manager)
    inference_helpers = InferenceHelpers(inference_engine)
    
    print("🚀 Phase 3 API Server started")
    print("📖 API Documentation: http://localhost:8000/docs")

# Model Management Endpoints
@app.post("/models/select", response_model=ModelSelectionResponse)
async def select_model(request: ModelSelectionRequest):
    """Select and load a model using intelligent selection"""
    
    # Convert request to internal format
    internal_request = {}
    
    if request.model:
        internal_request["model"] = request.model
    elif request.auto_select:
        internal_request["auto_select"] = True
    else:
        internal_request["priority"] = request.priority
        internal_request["capabilities"] = request.capabilities
    
    result = await model_manager.handle_request(internal_request)
    
    if result['status'] == 'success':
        return ModelSelectionResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get('reason', 'Selection failed'))

@app.post("/models/hot-load", response_model=HotLoadResponse)
async def hot_load_model(request: HotLoadRequest):
    """Hot load a new model into the system"""
    
    internal_request = {
        "hot_load": {
            "model_name": request.model_name,
            "model_config": request.model_config
        }
    }
    
    result = await model_manager.handle_request(internal_request)
    
    if result['status'] in ['hot_load_started', 'success']:
        return HotLoadResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get('reason', 'Hot loading failed'))

@app.get("/models/list", response_model=ModelLibraryResponse)
async def list_models():
    """List all available models"""
    
    result = await model_manager.handle_request({"list_models": True})
    
    if result['status'] == 'success':
        # Convert model specs to ModelInfo format
        models_info = {}
        for name, spec in result['models'].items():
            models_info[name] = ModelInfo(
                name=name,
                size_gb=spec['size_gb'],
                tier=ModelTier(spec['tier']),
                capabilities=[TaskCapability(cap) for cap in spec['capabilities']],
                load_time_estimate=0.1 * spec['size_gb'] if spec['tier'] == 'ram' else 0.5 * spec['size_gb']
            )
        
        return ModelLibraryResponse(
            status="success",
            models=models_info,
            total_models=result['total_models'],
            active_hot_loads=result['active_hot_loads']
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to retrieve model list")

@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get status of a background job (hot loading or tier move)"""
    
    # Try hot loading job first
    result = await model_manager.handle_request({"load_status": job_id})
    
    if result.get('status') != 'error':
        return JobStatusResponse(**result)
    
    # Try tier move job
    result = await model_manager.handle_request({"tier_job_status": job_id})
    
    if result.get('status') != 'error':
        return JobStatusResponse(**result)
    
    raise HTTPException(status_code=404, detail="Job not found")

# Tier Management Endpoints
@app.get("/tiers/status", response_model=TierStatusResponse)
async def get_tier_status():
    """Get current tier utilization status"""
    
    result = await model_manager.handle_request({"tier_status": True})
    
    if result['status'] == 'success':
        return TierStatusResponse(**result)
    else:
        raise HTTPException(status_code=500, detail="Failed to get tier status")

@app.post("/tiers/move", response_model=TierMoveResponse)
async def move_model_tier(request: TierMoveRequest):
    """Move a model between storage tiers"""
    
    internal_request = {
        "move_tier": {
            "model_name": request.model_name,
            "target_tier": request.target_tier
        }
    }
    
    result = await model_manager.handle_request(internal_request)
    
    if result['status'] == 'tier_move_started':
        return TierMoveResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get('reason', 'Tier move failed'))

@app.post("/tiers/optimize")
async def auto_optimize_tiers():
    """Automatically optimize model tier placement"""
    
    result = await model_manager.handle_request({"auto_optimize": True})
    
    if result['status'] == 'success':
        return {"status": "success", "optimizations": result['optimizations']}
    else:
        raise HTTPException(status_code=500, detail="Auto-optimization failed")

@app.put("/tiers/limits")
async def update_tier_limits(request: LimitsUpdateRequest):
    """Update tier allocation limits"""
    
    limits = {}
    if request.ram_max_gb is not None:
        limits["ram_max_gb"] = request.ram_max_gb
    if request.swap_max_gb is not None:
        limits["swap_max_gb"] = request.swap_max_gb
    if request.ram_reserved_gb is not None:
        limits["ram_reserved_gb"] = request.ram_reserved_gb
    
    result = await model_manager.handle_request({"update_limits": limits})
    
    if result['status'] == 'success':
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get('reason', 'Limit update failed'))

# Inference Endpoints
@app.post("/inference/generate", response_model=InferenceResponse)
async def generate_text(request: InferenceRequest):
    """Generate text using the optimal model"""
    
    config = InferenceConfig(
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        stream=request.stream
    )
    
    result = await inference_engine.generate_text(
        prompt=request.prompt,
        config=config,
        model_name=request.model
    )
    
    if result['status'] == 'success':
        return InferenceResponse(**result)
    else:
        raise HTTPException(status_code=400, detail=result.get('reason', 'Inference failed'))

@app.post("/inference/stream")
async def stream_generate_text(request: InferenceRequest):
    """Generate text with streaming response"""
    
    if not request.stream:
        request.stream = True  # Force streaming for this endpoint
    
    config = InferenceConfig(
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        top_p=request.top_p,
        stream=True
    )
    
    # Start streaming
    result = await inference_engine.generate_text(
        prompt=request.prompt,
        config=config,
        model_name=request.model
    )
    
    if result['status'] != 'streaming':
        raise HTTPException(status_code=400, detail=result.get('reason', 'Streaming failed'))
    
    model_name = result['model_used']
    
    async def generate_stream():
        async for chunk in inference_engine.stream_generate(request.prompt, config, model_name):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

# Convenience Endpoints
@app.post("/quick/generate")
async def quick_generate(prompt: str, max_tokens: int = 50):
    """Quick text generation with minimal configuration"""
    
    result = await inference_helpers.quick_generate(prompt, max_tokens)
    return {"generated_text": result}

@app.post("/quick/chat")
async def quick_chat(message: str):
    """Quick chat response"""
    
    result = await inference_helpers.chat_response(message)
    return {"response": result}

@app.post("/quick/code")
async def quick_code(description: str):
    """Quick code generation"""
    
    result = await inference_helpers.code_generation(description)
    return {"code": result}

# System Status Endpoints
@app.get("/system/status")
async def get_system_status():
    """Get comprehensive system status"""
    
    # Get tier status
    tier_result = await model_manager.handle_request({"tier_status": True})
    
    # Get model list
    models_result = await model_manager.handle_request({"list_models": True})
    
    # Get performance stats
    perf_stats = inference_engine.get_performance_stats()
    
    return {
        "status": "operational",
        "tiers": tier_result.get('tiers', {}),
        "models": {
            "total": models_result.get('total_models', 0),
            "active_loads": models_result.get('active_hot_loads', 0)
        },
        "performance": perf_stats
    }

@app.get("/system/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "version": "3.0.0"}

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {"status": "error", "reason": str(exc)}

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server"""
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    print("🚀 Starting Phase 3 REST API Server")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    run_server()
