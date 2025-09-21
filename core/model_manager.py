#!/usr/bin/env python3
"""
JetsonMind Model Manager
Advanced model loading/unloading with storage tier management
"""

import asyncio
import time
import psutil
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from inference_engine_v3 import ModelTier, ModelSpec

class ModelState(Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADING = "unloading"
    CACHED = "cached"

@dataclass
class ModelInstance:
    spec: ModelSpec
    state: ModelState
    loaded_at: Optional[float] = None
    last_used: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    location: Optional[str] = None  # RAM, SWAP, STORAGE

class JetsonModelManager:
    """Advanced model management with hot loading and storage tiers"""
    
    def __init__(self):
        self.models: Dict[str, ModelInstance] = {}
        self.memory_limit_gb = self._get_memory_limit()
        self.swap_limit_gb = self._get_swap_limit()
        self.storage_path = "/home/petr/jetson/data/models"
        self._ensure_storage_path()
        
    def _get_memory_limit(self) -> float:
        """Get system RAM limit"""
        return psutil.virtual_memory().total / (1024**3) * 0.8  # 80% of RAM
    
    def _get_swap_limit(self) -> float:
        """Get system swap limit"""
        swap = psutil.swap_memory()
        return swap.total / (1024**3) * 0.6 if swap.total > 0 else 0  # 60% of swap
    
    def _ensure_storage_path(self):
        """Ensure storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    async def load_model(self, model_name: str, force_tier: Optional[str] = None) -> Dict[str, any]:
        """Hot load model with intelligent tier placement"""
        if model_name not in self.models:
            return {"error": f"Model {model_name} not found in library"}
        
        model = self.models[model_name]
        
        if model.state == ModelState.LOADED:
            model.last_used = time.time()
            return {"status": "already_loaded", "location": model.location}
        
        # Set loading state
        model.state = ModelState.LOADING
        
        # Determine optimal tier
        target_tier = force_tier or await self._select_optimal_tier(model.spec)
        
        # Check if we need to free memory
        if target_tier in ["RAM", "SWAP"]:
            await self._ensure_memory_available(model.spec.size_gb, target_tier)
        
        # Simulate model loading (replace with actual loading logic)
        await asyncio.sleep(0.1)  # Simulate loading time
        
        # Update model state
        model.state = ModelState.LOADED
        model.loaded_at = time.time()
        model.last_used = time.time()
        model.location = target_tier
        model.memory_usage_mb = model.spec.size_gb * 1024
        
        return {
            "status": "loaded",
            "model": model_name,
            "location": target_tier,
            "size_gb": model.spec.size_gb,
            "load_time": 0.1
        }
    
    async def unload_model(self, model_name: str, to_storage: bool = False) -> Dict[str, any]:
        """Hot unload model with optional storage caching"""
        if model_name not in self.models:
            return {"error": f"Model {model_name} not found"}
        
        model = self.models[model_name]
        
        if model.state != ModelState.LOADED:
            return {"error": f"Model {model_name} not loaded"}
        
        model.state = ModelState.UNLOADING
        
        # Simulate unloading
        await asyncio.sleep(0.05)
        
        if to_storage:
            # Cache to storage
            model.state = ModelState.CACHED
            model.location = "STORAGE"
            model.memory_usage_mb = 0
        else:
            # Complete unload
            model.state = ModelState.UNLOADED
            model.location = None
            model.memory_usage_mb = 0
            model.loaded_at = None
        
        return {
            "status": "unloaded",
            "model": model_name,
            "cached_to_storage": to_storage
        }
    
    async def _select_optimal_tier(self, spec: ModelSpec) -> str:
        """Select optimal memory tier for model"""
        current_ram_usage = self._get_current_ram_usage()
        current_swap_usage = self._get_current_swap_usage()
        
        # Check if model fits in RAM
        if current_ram_usage + spec.size_gb <= self.memory_limit_gb:
            return "RAM"
        
        # Check if model fits in SWAP
        if current_swap_usage + spec.size_gb <= self.swap_limit_gb:
            return "SWAP"
        
        # Default to storage
        return "STORAGE"
    
    async def _ensure_memory_available(self, required_gb: float, tier: str):
        """Free memory if needed for new model"""
        if tier == "RAM":
            current_usage = self._get_current_ram_usage()
            if current_usage + required_gb > self.memory_limit_gb:
                await self._free_memory(required_gb, "RAM")
        
        elif tier == "SWAP":
            current_usage = self._get_current_swap_usage()
            if current_usage + required_gb > self.swap_limit_gb:
                await self._free_memory(required_gb, "SWAP")
    
    async def _free_memory(self, required_gb: float, tier: str):
        """Free memory by unloading least recently used models"""
        candidates = [
            (name, model) for name, model in self.models.items()
            if model.state == ModelState.LOADED and model.location == tier
        ]
        
        # Sort by last used (oldest first)
        candidates.sort(key=lambda x: x[1].last_used or 0)
        
        freed_gb = 0
        for name, model in candidates:
            if freed_gb >= required_gb:
                break
            
            await self.unload_model(name, to_storage=True)
            freed_gb += model.spec.size_gb
    
    def _get_current_ram_usage(self) -> float:
        """Get current RAM usage by loaded models"""
        return sum(
            model.spec.size_gb for model in self.models.values()
            if model.state == ModelState.LOADED and model.location == "RAM"
        )
    
    def _get_current_swap_usage(self) -> float:
        """Get current SWAP usage by loaded models"""
        return sum(
            model.spec.size_gb for model in self.models.values()
            if model.state == ModelState.LOADED and model.location == "SWAP"
        )
    
    def get_memory_status(self) -> Dict[str, any]:
        """Get comprehensive memory status"""
        system_ram = psutil.virtual_memory()
        system_swap = psutil.swap_memory()
        
        loaded_models = {
            name: {
                "location": model.location,
                "size_gb": model.spec.size_gb,
                "last_used": model.last_used
            }
            for name, model in self.models.items()
            if model.state == ModelState.LOADED
        }
        
        return {
            "system": {
                "ram_total_gb": system_ram.total / (1024**3),
                "ram_available_gb": system_ram.available / (1024**3),
                "swap_total_gb": system_swap.total / (1024**3),
                "swap_used_gb": system_swap.used / (1024**3)
            },
            "jetsonmind": {
                "ram_limit_gb": self.memory_limit_gb,
                "swap_limit_gb": self.swap_limit_gb,
                "ram_used_gb": self._get_current_ram_usage(),
                "swap_used_gb": self._get_current_swap_usage(),
                "loaded_models": loaded_models
            }
        }
    
    def register_model(self, name: str, spec: ModelSpec):
        """Register model in manager"""
        self.models[name] = ModelInstance(
            spec=spec,
            state=ModelState.UNLOADED
        )
    
    async def optimize_memory(self, strategy: str = "balanced") -> Dict[str, any]:
        """Optimize memory usage with different strategies"""
        if strategy == "aggressive":
            # Keep only most recently used model
            loaded = [(name, model) for name, model in self.models.items() 
                     if model.state == ModelState.LOADED]
            
            if len(loaded) > 1:
                # Sort by last used, keep most recent
                loaded.sort(key=lambda x: x[1].last_used or 0, reverse=True)
                
                unloaded = []
                for name, model in loaded[1:]:  # Unload all but most recent
                    await self.unload_model(name, to_storage=True)
                    unloaded.append(name)
                
                return {"strategy": "aggressive", "unloaded": unloaded}
        
        elif strategy == "balanced":
            # Move SWAP models to storage if RAM available
            swap_models = [(name, model) for name, model in self.models.items()
                          if model.state == ModelState.LOADED and model.location == "SWAP"]
            
            moved = []
            for name, model in swap_models:
                if self._get_current_ram_usage() + model.spec.size_gb <= self.memory_limit_gb:
                    await self.unload_model(name)
                    await self.load_model(name, force_tier="RAM")
                    moved.append(f"{name}: SWAP->RAM")
                else:
                    await self.unload_model(name, to_storage=True)
                    moved.append(f"{name}: SWAP->STORAGE")
            
            return {"strategy": "balanced", "optimizations": moved}
        
        return {"strategy": strategy, "status": "completed"}
    
    def hot_swap_models(self, source_model: str, target_model: str):
        """Instant model swapping"""
        if source_model in self.models and target_model in self.models:
            return f"Swapped {source_model} -> {target_model} (simulated)"
        return f"Model not found: {source_model} or {target_model}"

# Global model manager instance
model_manager = JetsonModelManager()
