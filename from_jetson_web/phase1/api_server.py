#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uvicorn
import json
import time
from typing import List, Optional, Dict, Any
import logging

# Import our enhanced components
from enhanced_model_server import EnhancedAIServer
from performance_optimizer import AdvancedMonitor, ModelOptimizer, PerformanceProfiler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class InferenceRequest(BaseModel):
    prompt: str
    model_preference: Optional[str] = None
    max_length: Optional[int] = 50
    temperature: Optional[float] = 0.7
    user_id: Optional[str] = None

class BatchInferenceRequest(BaseModel):
    prompts: List[str]
    model_preference: Optional[str] = None
    max_length: Optional[int] = 50
    temperature: Optional[float] = 0.7
    user_id: Optional[str] = None

class ModelLoadRequest(BaseModel):
    model_name: str
    priority: Optional[str] = "normal"

class InferenceResponse(BaseModel):
    response: str
    model_used: str
    inference_time: float
    tokens_generated: int
    tokens_per_second: float
    timestamp: float

class SystemStatus(BaseModel):
    active_models: List[str]
    memory_usage_gb: float
    memory_budget_gb: float
    swap_cache_size: int
    queue_size: int
    cpu_percent: float
    gpu_memory_gb: float
    temperature_c: float
    alerts: List[Dict[str, Any]]

class ProductionAIServer:
    def __init__(self):
        self.app = FastAPI(
            title="Enhanced Jetson AI Server",
            description="Production-ready multi-model AI inference server",
            version="2.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.ai_server = None
        self.monitor = None
        self.optimizer = None
        self.profiler = None
        
        # Setup routes
        self.setup_routes()
        
        # Background tasks
        self.background_tasks = set()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize system on startup"""
            logger.info("Starting Enhanced AI Server...")
            
            # Initialize components
            self.ai_server = EnhancedAIServer()
            self.monitor = AdvancedMonitor()
            self.optimizer = ModelOptimizer(self.ai_server.model_pool)
            self.profiler = PerformanceProfiler()
            
            # Start background tasks
            task1 = asyncio.create_task(self.ai_server.start_batch_processor())
            task2 = asyncio.create_task(self.monitor.start_monitoring())
            task3 = asyncio.create_task(self.optimization_loop())
            
            self.background_tasks.update([task1, task2, task3])
            
            # Preload common models
            common_models = [
                "Qwen/Qwen2.5-0.5B-Instruct",
                "Qwen/Qwen2.5-1.5B-Instruct"
            ]
            
            try:
                await self.ai_server.preload_models(common_models)
                logger.info(f"Preloaded {len(common_models)} models")
            except Exception as e:
                logger.warning(f"Failed to preload some models: {e}")
            
            logger.info("Enhanced AI Server started successfully!")
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Cleanup on shutdown"""
            logger.info("Shutting down Enhanced AI Server...")
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Stop monitoring
            if self.monitor:
                self.monitor.monitoring = False
            
            logger.info("Enhanced AI Server shut down complete")
        
        @self.app.post("/inference", response_model=InferenceResponse)
        async def inference_endpoint(request: InferenceRequest):
            """Single inference endpoint"""
            try:
                start_time = time.time()
                
                result = await self.ai_server.inference(
                    request.prompt, 
                    request.model_preference
                )
                
                inference_time = time.time() - start_time
                
                # Estimate tokens (rough approximation)
                tokens_generated = len(result['response'].split())
                tokens_per_second = tokens_generated / inference_time if inference_time > 0 else 0
                
                # Record performance
                self.profiler.record_inference(
                    result['model'], 
                    inference_time, 
                    tokens_generated
                )
                
                return InferenceResponse(
                    response=result['response'],
                    model_used=result['model'],
                    inference_time=inference_time,
                    tokens_generated=tokens_generated,
                    tokens_per_second=tokens_per_second,
                    timestamp=result['timestamp']
                )
                
            except Exception as e:
                logger.error(f"Inference error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/batch_inference")
        async def batch_inference_endpoint(request: BatchInferenceRequest):
            """Batch inference endpoint"""
            try:
                start_time = time.time()
                
                # Process batch through router
                tasks = []
                for prompt in request.prompts:
                    task = self.ai_server.inference(prompt, request.model_preference)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
                
                total_time = time.time() - start_time
                
                return {
                    "results": results,
                    "batch_size": len(request.prompts),
                    "total_time": total_time,
                    "avg_time_per_request": total_time / len(request.prompts)
                }
                
            except Exception as e:
                logger.error(f"Batch inference error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/load_model")
        async def load_model_endpoint(request: ModelLoadRequest):
            """Load specific model"""
            try:
                start_time = time.time()
                
                await self.ai_server.model_pool.load_model_smart(
                    request.model_name, 
                    request.priority
                )
                
                load_time = time.time() - start_time
                
                return {
                    "message": f"Model {request.model_name} loaded successfully",
                    "load_time": load_time
                }
                
            except Exception as e:
                logger.error(f"Model loading error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/status", response_model=SystemStatus)
        async def status_endpoint():
            """Get system status"""
            try:
                server_status = self.ai_server.get_status()
                
                # Get latest metrics
                latest_metrics = None
                if self.monitor.metrics_history:
                    latest_metrics = self.monitor.metrics_history[-1]
                
                return SystemStatus(
                    active_models=server_status['active_models'],
                    memory_usage_gb=server_status['memory_usage_gb'],
                    memory_budget_gb=server_status['memory_budget_gb'],
                    swap_cache_size=server_status['swap_cache_size'],
                    queue_size=server_status['queue_size'],
                    cpu_percent=latest_metrics['cpu_percent'] if latest_metrics else 0,
                    gpu_memory_gb=latest_metrics['gpu_memory_allocated'] / 1024**3 if latest_metrics else 0,
                    temperature_c=latest_metrics['cpu_temp'] if latest_metrics else 0,
                    alerts=self.monitor.system_alerts[-10:]  # Last 10 alerts
                )
                
            except Exception as e:
                logger.error(f"Status error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/performance")
        async def performance_endpoint():
            """Get performance analytics"""
            try:
                return {
                    "system_report": self.profiler.get_system_performance_report(),
                    "recent_performance": self.monitor.get_performance_summary(),
                    "optimization_history": self.optimizer.optimization_history[-10:]
                }
                
            except Exception as e:
                logger.error(f"Performance error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/models")
        async def models_endpoint():
            """List available and loaded models"""
            try:
                active_models = {}
                for name, data in self.ai_server.model_pool.active_models.items():
                    active_models[name] = {
                        "memory_size_gb": data['memory_size'] / 1024**3,
                        "load_time": data['load_time'],
                        "usage_count": data['usage_count'],
                        "last_used": data['last_used'],
                        "priority": data['priority']
                    }
                
                return {
                    "active_models": active_models,
                    "swap_cache": list(self.ai_server.model_pool.swap_cache.keys()),
                    "model_capabilities": self.ai_server.router.model_capabilities
                }
                
            except Exception as e:
                logger.error(f"Models error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/optimize")
        async def optimize_endpoint(background_tasks: BackgroundTasks):
            """Trigger manual optimization"""
            try:
                background_tasks.add_task(self.optimizer.optimize_model_placement)
                return {"message": "Optimization triggered"}
                
            except Exception as e:
                logger.error(f"Optimization error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_endpoint():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "version": "2.0.0"
            }
    
    async def optimization_loop(self):
        """Background optimization loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Optimize every minute
                await self.optimizer.optimize_model_placement()
                
                # Record optimization
                self.optimizer.optimization_history.append({
                    "timestamp": time.time(),
                    "active_models": len(self.ai_server.model_pool.active_models),
                    "memory_usage": self.ai_server.model_pool.get_memory_usage() / 1024**3
                })
                
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
    
    def run(self, host="0.0.0.0", port=8000):
        """Run the server"""
        uvicorn.run(self.app, host=host, port=port)

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Jetson AI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    
    # Create and run server
    server = ProductionAIServer()
    
    print(f"""
🚀 Enhanced Jetson AI Server Starting...

📡 API Endpoints:
   POST /inference          - Single inference
   POST /batch_inference    - Batch inference  
   POST /load_model        - Load specific model
   GET  /status            - System status
   GET  /performance       - Performance analytics
   GET  /models            - Model information
   POST /optimize          - Trigger optimization
   GET  /health            - Health check

🌐 Server URL: http://{args.host}:{args.port}
📚 API Docs: http://{args.host}:{args.port}/docs

Starting server...
    """)
    
    server.run(host=args.host, port=args.port)
