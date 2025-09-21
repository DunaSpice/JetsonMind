#!/usr/bin/env python3
"""
Phase 3: Client SDK
Easy-to-use Python SDK for the model management and inference API
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass

@dataclass
class ModelInfo:
    name: str
    size_gb: float
    tier: str
    capabilities: List[str]
    load_time_estimate: float

class ModelManagementClient:
    """Client for model management operations"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    return await response.json()
            else:
                async with self.session.request(method, url, json=data) as response:
                    return await response.json()
        except Exception as e:
            return {"status": "error", "reason": f"Request failed: {str(e)}"}
    
    # Model Management Methods
    async def select_model(self, model: Optional[str] = None, 
                          priority: str = "balanced", 
                          capabilities: List[str] = None) -> Dict:
        """Select and load a model"""
        data = {
            "priority": priority,
            "capabilities": capabilities or ["text-generation"]
        }
        
        if model:
            data["model"] = model
        else:
            data["auto_select"] = True
        
        return await self._request("POST", "/models/select", data)
    
    async def hot_load_model(self, model_name: str, size_gb: float, 
                            tier: str = "ram", capabilities: List[str] = None) -> Dict:
        """Hot load a new model"""
        data = {
            "model_name": model_name,
            "model_config": {
                "size_gb": size_gb,
                "tier": tier,
                "capabilities": capabilities or ["text-generation"]
            }
        }
        
        return await self._request("POST", "/models/hot-load", data)
    
    async def list_models(self) -> List[ModelInfo]:
        """List all available models"""
        result = await self._request("GET", "/models/list")
        
        if result.get("status") == "success":
            models = []
            for name, info in result["models"].items():
                models.append(ModelInfo(
                    name=name,
                    size_gb=info["size_gb"],
                    tier=info["tier"],
                    capabilities=info["capabilities"],
                    load_time_estimate=info["load_time_estimate"]
                ))
            return models
        else:
            return []
    
    async def get_job_status(self, job_id: str) -> Dict:
        """Get status of background job"""
        return await self._request("GET", f"/jobs/{job_id}")
    
    # Tier Management Methods
    async def get_tier_status(self) -> Dict:
        """Get tier utilization status"""
        return await self._request("GET", "/tiers/status")
    
    async def move_model_tier(self, model_name: str, target_tier: str) -> Dict:
        """Move model between tiers"""
        data = {
            "model_name": model_name,
            "target_tier": target_tier
        }
        
        return await self._request("POST", "/tiers/move", data)
    
    async def auto_optimize_tiers(self) -> Dict:
        """Auto-optimize tier placement"""
        return await self._request("POST", "/tiers/optimize")
    
    async def update_tier_limits(self, ram_max_gb: Optional[float] = None,
                                swap_max_gb: Optional[float] = None,
                                ram_reserved_gb: Optional[float] = None) -> Dict:
        """Update tier limits"""
        data = {}
        if ram_max_gb is not None:
            data["ram_max_gb"] = ram_max_gb
        if swap_max_gb is not None:
            data["swap_max_gb"] = swap_max_gb
        if ram_reserved_gb is not None:
            data["ram_reserved_gb"] = ram_reserved_gb
        
        return await self._request("PUT", "/tiers/limits", data)

class InferenceClient:
    """Client for inference operations"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data) as response:
                return await response.json()
        except Exception as e:
            return {"status": "error", "reason": f"Request failed: {str(e)}"}
    
    # Inference Methods
    async def generate_text(self, prompt: str, model: Optional[str] = None,
                           max_tokens: int = 100, temperature: float = 0.7,
                           top_p: float = 0.9) -> Dict:
        """Generate text"""
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False
        }
        
        if model:
            data["model"] = model
        
        return await self._request("POST", "/inference/generate", data)
    
    async def stream_generate_text(self, prompt: str, model: Optional[str] = None,
                                  max_tokens: int = 100, temperature: float = 0.7,
                                  top_p: float = 0.9) -> AsyncGenerator[Dict, None]:
        """Generate text with streaming"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": True
        }
        
        if model:
            data["model"] = model
        
        url = f"{self.base_url}/inference/stream"
        
        async with self.session.post(url, json=data) as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    if data_str == '[DONE]':
                        break
                    try:
                        yield json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
    
    # Convenience Methods
    async def quick_generate(self, prompt: str, max_tokens: int = 50) -> str:
        """Quick text generation"""
        result = await self._request("POST", "/quick/generate", {
            "prompt": prompt,
            "max_tokens": max_tokens
        })
        return result.get("generated_text", "")
    
    async def chat(self, message: str) -> str:
        """Quick chat response"""
        result = await self._request("POST", "/quick/chat", {"message": message})
        return result.get("response", "")
    
    async def generate_code(self, description: str) -> str:
        """Quick code generation"""
        result = await self._request("POST", "/quick/code", {"description": description})
        return result.get("code", "")

class SystemClient:
    """Client for system status and health"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str) -> Dict:
        """Make HTTP request to API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.get(url) as response:
                return await response.json()
        except Exception as e:
            return {"status": "error", "reason": f"Request failed: {str(e)}"}
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        return await self._request("GET", "/system/status")
    
    async def health_check(self) -> Dict:
        """Simple health check"""
        return await self._request("GET", "/system/health")

# Unified Client
class Phase3Client:
    """Unified client for all Phase 3 operations"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.models = ModelManagementClient(base_url)
        self.inference = InferenceClient(base_url)
        self.system = SystemClient(base_url)
    
    async def __aenter__(self):
        await self.models.__aenter__()
        await self.inference.__aenter__()
        await self.system.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.models.__aexit__(exc_type, exc_val, exc_tb)
        await self.inference.__aexit__(exc_type, exc_val, exc_tb)
        await self.system.__aexit__(exc_type, exc_val, exc_tb)

# Usage Examples
async def demo_client_sdk():
    """Demonstrate client SDK usage"""
    print("🔌 Phase 3: Client SDK Demo")
    print("=" * 40)
    
    # Note: This demo shows usage patterns, but won't connect to actual server
    print("📝 Example usage patterns:")
    
    print("\n1. Model Management:")
    print("""
async with Phase3Client() as client:
    # List models
    models = await client.models.list_models()
    
    # Select optimal model
    result = await client.models.select_model(priority="speed")
    
    # Hot load new model
    result = await client.models.hot_load_model(
        "custom-model", size_gb=2.0, tier="ram"
    )
""")
    
    print("\n2. Inference:")
    print("""
async with Phase3Client() as client:
    # Generate text
    result = await client.inference.generate_text(
        "The future of AI is", max_tokens=50
    )
    
    # Quick chat
    response = await client.inference.chat("Hello!")
    
    # Stream generation
    async for chunk in client.inference.stream_generate_text("Tell me about"):
        print(chunk["text"], end="")
""")
    
    print("\n3. Tier Management:")
    print("""
async with Phase3Client() as client:
    # Check tier status
    status = await client.models.get_tier_status()
    
    # Move model to RAM for better performance
    result = await client.models.move_model_tier("gpt-j-6b", "ram")
    
    # Auto-optimize
    result = await client.models.auto_optimize_tiers()
""")
    
    print("\n4. System Monitoring:")
    print("""
async with Phase3Client() as client:
    # System status
    status = await client.system.get_system_status()
    
    # Health check
    health = await client.system.health_check()
""")

if __name__ == "__main__":
    asyncio.run(demo_client_sdk())
