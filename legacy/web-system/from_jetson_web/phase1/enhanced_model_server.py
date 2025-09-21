#!/usr/bin/env python3
import asyncio
import torch
import time
import json
import psutil
import gc
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import pickle
import os

class EnhancedModelPool:
    def __init__(self, ram_budget_gb=5.5, swap_dir="/tmp/model_swap"):
        self.ram_budget = ram_budget_gb * 1024**3  # Convert to bytes
        self.swap_dir = swap_dir
        self.active_models = {}
        self.model_queue = {}
        self.swap_cache = {}
        self.executor = ThreadPoolExecutor(max_workers=6)
        self.request_stats = {}
        
        os.makedirs(swap_dir, exist_ok=True)
        
    def get_memory_usage(self):
        return sum(model['memory_size'] for model in self.active_models.values())
    
    async def load_model_smart(self, model_name, priority="normal"):
        """Smart model loading with automatic memory management"""
        if model_name in self.active_models:
            self.active_models[model_name]['last_used'] = time.time()
            return self.active_models[model_name]['model'], self.active_models[model_name]['tokenizer']
        
        # Check if we need to free memory
        estimated_size = self.estimate_model_size(model_name)
        if self.get_memory_usage() + estimated_size > self.ram_budget:
            await self.free_memory_for_model(estimated_size, priority)
        
        # Load model
        start_time = time.time()
        
        # Check swap cache first
        if model_name in self.swap_cache:
            model, tokenizer = await self.load_from_swap(model_name)
        else:
            model, tokenizer = await self.load_from_huggingface(model_name)
        
        load_time = time.time() - start_time
        memory_size = self.measure_model_memory(model)
        
        self.active_models[model_name] = {
            'model': model,
            'tokenizer': tokenizer,
            'memory_size': memory_size,
            'load_time': load_time,
            'last_used': time.time(),
            'usage_count': 0,
            'priority': priority
        }
        
        return model, tokenizer
    
    async def load_from_huggingface(self, model_name):
        """Load model from HuggingFace with optimization"""
        loop = asyncio.get_event_loop()
        
        def _load():
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="cuda",
                low_cpu_mem_usage=True
            )
            return model, tokenizer
        
        return await loop.run_in_executor(self.executor, _load)
    
    async def load_from_swap(self, model_name):
        """Fast load from swap cache"""
        swap_path = os.path.join(self.swap_dir, f"{model_name.replace('/', '_')}.pkl")
        
        loop = asyncio.get_event_loop()
        
        def _load_swap():
            with open(swap_path, 'rb') as f:
                return pickle.load(f)
        
        return await loop.run_in_executor(self.executor, _load_swap)
    
    async def save_to_swap(self, model_name):
        """Save model to swap for fast reload"""
        if model_name not in self.active_models:
            return
        
        model_data = self.active_models[model_name]
        swap_path = os.path.join(self.swap_dir, f"{model_name.replace('/', '_')}.pkl")
        
        loop = asyncio.get_event_loop()
        
        def _save_swap():
            with open(swap_path, 'wb') as f:
                pickle.dump((model_data['model'], model_data['tokenizer']), f)
        
        await loop.run_in_executor(self.executor, _save_swap)
        self.swap_cache[model_name] = swap_path
    
    async def free_memory_for_model(self, needed_size, priority):
        """Intelligent memory freeing based on usage patterns"""
        candidates = []
        
        for name, data in self.active_models.items():
            if data['priority'] == "high" and priority != "high":
                continue  # Don't evict high priority models for normal requests
            
            score = self.calculate_eviction_score(data)
            candidates.append((score, name, data))
        
        # Sort by eviction score (higher = more likely to evict)
        candidates.sort(reverse=True)
        
        freed_memory = 0
        for score, name, data in candidates:
            if freed_memory >= needed_size:
                break
            
            # Save to swap before evicting
            await self.save_to_swap(name)
            
            # Free memory
            del data['model'], data['tokenizer']
            torch.cuda.empty_cache()
            gc.collect()
            
            freed_memory += data['memory_size']
            del self.active_models[name]
    
    def calculate_eviction_score(self, model_data):
        """Calculate eviction score (higher = more likely to evict)"""
        time_since_use = time.time() - model_data['last_used']
        usage_frequency = model_data['usage_count']
        memory_size = model_data['memory_size']
        
        # Prefer evicting: old, unused, large models
        score = time_since_use * 0.5 + memory_size / (usage_frequency + 1) * 0.3
        
        if model_data['priority'] == "low":
            score *= 2
        elif model_data['priority'] == "high":
            score *= 0.1
        
        return score
    
    def estimate_model_size(self, model_name):
        """Estimate model memory size based on name"""
        size_estimates = {
            "0.5B": 1.0 * 1024**3,
            "1B": 2.0 * 1024**3,
            "1.5B": 3.0 * 1024**3,
            "3B": 6.0 * 1024**3,
            "7B": 14.0 * 1024**3
        }
        
        for size_key, size_bytes in size_estimates.items():
            if size_key in model_name:
                return size_bytes
        
        return 2.0 * 1024**3  # Default estimate
    
    def measure_model_memory(self, model):
        """Measure actual model memory usage"""
        return sum(p.numel() * p.element_size() for p in model.parameters())
    
    async def inference_batch(self, model_name, prompts, max_length=50):
        """Batch inference for better throughput"""
        model, tokenizer = await self.load_model_smart(model_name)
        
        # Update usage stats
        self.active_models[model_name]['usage_count'] += len(prompts)
        self.active_models[model_name]['last_used'] = time.time()
        
        # Batch tokenization
        inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True).to("cuda")
        
        # Batch inference
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=inputs['input_ids'].shape[1] + max_length,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id,
                num_return_sequences=1
            )
        
        # Decode results
        results = []
        for i, output in enumerate(outputs):
            result = tokenizer.decode(output, skip_special_tokens=True)
            # Remove input prompt from result
            result = result[len(prompts[i]):].strip()
            results.append(result)
        
        return results

class IntelligentRouter:
    def __init__(self, model_pool):
        self.model_pool = model_pool
        self.model_capabilities = {
            "Qwen/Qwen2.5-0.5B-Instruct": ["general", "chat", "simple"],
            "Qwen/Qwen2.5-1.5B-Instruct": ["coding", "analysis", "medium"],
            "Qwen/Qwen2.5-3B-Instruct": ["complex", "reasoning", "large"],
            "microsoft/DialoGPT-small": ["conversation", "chat"],
            "microsoft/CodeBERT-base": ["code", "programming"]
        }
        
        self.request_patterns = {}
    
    def analyze_request_complexity(self, prompt):
        """Analyze request to determine optimal model"""
        prompt_lower = prompt.lower()
        
        # Code-related keywords
        if any(word in prompt_lower for word in ["code", "function", "python", "javascript", "programming"]):
            return "coding", "medium"
        
        # Complex reasoning keywords
        if any(word in prompt_lower for word in ["analyze", "explain", "complex", "detailed", "reasoning"]):
            return "complex", "high"
        
        # Simple chat/general
        if len(prompt.split()) < 10:
            return "simple", "low"
        
        return "general", "normal"
    
    async def route_request(self, prompt, user_preference=None):
        """Intelligently route request to best available model"""
        task_type, complexity = self.analyze_request_complexity(prompt)
        
        # Find best model for task
        best_model = None
        best_score = 0
        
        for model_name, capabilities in self.model_capabilities.items():
            score = 0
            
            # Task match bonus
            if task_type in capabilities:
                score += 10
            
            # Complexity match bonus
            if complexity in capabilities:
                score += 5
            
            # Availability bonus (already loaded models get preference)
            if model_name in self.model_pool.active_models:
                score += 3
            
            # User preference bonus
            if user_preference and user_preference in model_name:
                score += 2
            
            if score > best_score:
                best_score = score
                best_model = model_name
        
        # Fallback to default model
        if not best_model:
            best_model = "Qwen/Qwen2.5-0.5B-Instruct"
        
        return best_model

class EnhancedAIServer:
    def __init__(self):
        self.model_pool = EnhancedModelPool()
        self.router = IntelligentRouter(self.model_pool)
        self.request_queue = asyncio.Queue()
        self.batch_size = 4
        self.batch_timeout = 0.1  # 100ms
        
    async def start_batch_processor(self):
        """Process requests in batches for better throughput"""
        while True:
            batch = []
            batch_start = time.time()
            
            # Collect batch
            while len(batch) < self.batch_size and (time.time() - batch_start) < self.batch_timeout:
                try:
                    request = await asyncio.wait_for(self.request_queue.get(), timeout=0.01)
                    batch.append(request)
                except asyncio.TimeoutError:
                    break
            
            if batch:
                await self.process_batch(batch)
    
    async def process_batch(self, batch):
        """Process a batch of requests"""
        # Group by model
        model_batches = {}
        for request in batch:
            model_name = await self.router.route_request(request['prompt'])
            if model_name not in model_batches:
                model_batches[model_name] = []
            model_batches[model_name].append(request)
        
        # Process each model batch
        tasks = []
        for model_name, requests in model_batches.items():
            prompts = [req['prompt'] for req in requests]
            task = self.process_model_batch(model_name, prompts, requests)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def process_model_batch(self, model_name, prompts, requests):
        """Process batch for specific model"""
        try:
            results = await self.model_pool.inference_batch(model_name, prompts)
            
            for request, result in zip(requests, results):
                request['future'].set_result({
                    'response': result,
                    'model': model_name,
                    'timestamp': time.time()
                })
        except Exception as e:
            for request in requests:
                request['future'].set_exception(e)
    
    async def inference(self, prompt, user_preference=None):
        """Public inference API"""
        future = asyncio.Future()
        request = {
            'prompt': prompt,
            'user_preference': user_preference,
            'future': future,
            'timestamp': time.time()
        }
        
        await self.request_queue.put(request)
        return await future
    
    async def preload_models(self, model_list):
        """Preload commonly used models"""
        tasks = []
        for model_name in model_list:
            task = self.model_pool.load_model_smart(model_name, priority="high")
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_status(self):
        """Get server status"""
        return {
            'active_models': list(self.model_pool.active_models.keys()),
            'memory_usage_gb': self.model_pool.get_memory_usage() / 1024**3,
            'memory_budget_gb': self.model_pool.ram_budget / 1024**3,
            'swap_cache_size': len(self.model_pool.swap_cache),
            'queue_size': self.request_queue.qsize()
        }

# Usage example
async def main():
    server = EnhancedAIServer()
    
    # Start batch processor
    asyncio.create_task(server.start_batch_processor())
    
    # Preload common models
    common_models = [
        "Qwen/Qwen2.5-0.5B-Instruct",
        "Qwen/Qwen2.5-1.5B-Instruct"
    ]
    await server.preload_models(common_models)
    
    # Example requests
    tasks = [
        server.inference("Write a Python function to sort a list"),
        server.inference("What is the weather like?"),
        server.inference("Explain quantum computing in simple terms"),
        server.inference("Hello, how are you?")
    ]
    
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results):
        print(f"Request {i+1}: {result['response'][:100]}...")
        print(f"Model used: {result['model']}")
        print()
    
    print("Server status:", server.get_status())

if __name__ == "__main__":
    asyncio.run(main())
