#!/usr/bin/env python3
"""
Phase 3: Inference Engine
User-friendly inference with automatic model selection and optimization
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass

@dataclass
class InferenceConfig:
    max_tokens: int = 100
    temperature: float = 0.7
    top_p: float = 0.9
    stream: bool = False

class InferenceEngine:
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.inference_cache = {}
        self.performance_stats = {}
    
    async def generate_text(self, prompt: str, config: InferenceConfig, 
                           model_name: Optional[str] = None) -> Dict:
        """Generate text with automatic model selection and optimization"""
        start_time = time.time()
        
        # Step 1: Select optimal model if not specified
        if not model_name:
            selection_result = await self._select_optimal_model(prompt, config)
            if selection_result['status'] != 'success':
                return selection_result
            model_name = selection_result['model']
        else:
            # Ensure specified model is loaded
            selection_result = await self.model_manager.handle_request({"model": model_name})
            if selection_result['status'] != 'success':
                return {"status": "error", "reason": f"Model '{model_name}' unavailable"}
        
        # Step 2: Execute inference
        try:
            if config.stream:
                return await self._stream_inference(prompt, config, model_name, start_time)
            else:
                return await self._batch_inference(prompt, config, model_name, start_time)
        
        except Exception as e:
            return {
                "status": "error",
                "reason": f"Inference failed: {str(e)}",
                "model_used": model_name
            }
    
    async def _select_optimal_model(self, prompt: str, config: InferenceConfig) -> Dict:
        """Intelligently select model based on prompt and config"""
        
        # Analyze prompt characteristics
        prompt_length = len(prompt.split())
        
        # Determine optimal selection criteria
        if config.stream or prompt_length > 100:
            # Long prompts or streaming prefer quality
            priority = "quality"
        elif config.temperature < 0.3:
            # Low temperature suggests precision tasks
            priority = "balanced"
        else:
            # Default to speed for interactive use
            priority = "speed"
        
        # Detect task type from prompt
        capabilities = self._detect_capabilities(prompt)
        
        # Request optimal model
        return await self.model_manager.handle_request({
            "priority": priority,
            "capabilities": capabilities
        })
    
    def _detect_capabilities(self, prompt: str) -> List[str]:
        """Detect required capabilities from prompt"""
        prompt_lower = prompt.lower()
        capabilities = ["text-generation"]  # Default
        
        # Classification indicators
        if any(word in prompt_lower for word in ["classify", "category", "sentiment", "label"]):
            capabilities.append("text-classification")
        
        # Code generation indicators
        if any(word in prompt_lower for word in ["code", "function", "python", "javascript", "def ", "class "]):
            capabilities.append("code-generation")
        
        # Chat indicators
        if any(word in prompt_lower for word in ["hello", "hi", "how are you", "chat", "conversation"]):
            capabilities.append("chat")
        
        return capabilities
    
    async def _batch_inference(self, prompt: str, config: InferenceConfig, 
                              model_name: str, start_time: float) -> Dict:
        """Execute batch inference"""
        
        # Simulate inference with realistic timing
        model_info = self.model_manager.base_server.model_library.get(model_name)
        if not model_info:
            return {"status": "error", "reason": "Model not found"}
        
        # Inference time based on model size and token count
        base_time = 0.1 if model_info.tier.value == "ram" else 0.3
        inference_time = base_time * (config.max_tokens / 50)  # Scale with tokens
        
        await asyncio.sleep(inference_time)
        
        # Generate mock response
        generated_text = self._generate_mock_text(prompt, config.max_tokens)
        total_time = time.time() - start_time
        
        # Update performance stats
        self._update_performance_stats(model_name, total_time, len(generated_text.split()))
        
        return {
            "status": "success",
            "model_used": model_name,
            "generated_text": generated_text,
            "tokens_generated": len(generated_text.split()),
            "inference_time_ms": total_time * 1000,
            "model_tier": model_info.tier.value
        }
    
    async def _stream_inference(self, prompt: str, config: InferenceConfig, 
                               model_name: str, start_time: float) -> Dict:
        """Execute streaming inference"""
        
        # For streaming, return generator info
        return {
            "status": "streaming",
            "model_used": model_name,
            "stream_id": f"stream_{int(time.time())}",
            "estimated_tokens": config.max_tokens
        }
    
    async def stream_generate(self, prompt: str, config: InferenceConfig, 
                             model_name: str) -> AsyncGenerator[Dict, None]:
        """Generate streaming response"""
        
        model_info = self.model_manager.base_server.model_library.get(model_name)
        chunk_delay = 0.05 if model_info.tier.value == "ram" else 0.1
        
        # Generate text in chunks
        full_text = self._generate_mock_text(prompt, config.max_tokens)
        words = full_text.split()
        
        chunk_id = 0
        tokens_so_far = 0
        
        for i in range(0, len(words), 3):  # 3 words per chunk
            chunk_words = words[i:i+3]
            chunk_text = " ".join(chunk_words)
            tokens_so_far += len(chunk_words)
            
            yield {
                "chunk_id": chunk_id,
                "text": chunk_text + " ",
                "is_final": i + 3 >= len(words),
                "tokens_so_far": tokens_so_far
            }
            
            chunk_id += 1
            await asyncio.sleep(chunk_delay)
    
    def _generate_mock_text(self, prompt: str, max_tokens: int) -> str:
        """Generate mock text response"""
        
        # Simple mock generation based on prompt
        if "code" in prompt.lower():
            return f"def example_function():\n    # Generated code based on: {prompt[:50]}...\n    return 'Hello, World!'"
        
        elif "classify" in prompt.lower():
            return "Classification: Positive (confidence: 0.87)"
        
        elif any(greeting in prompt.lower() for greeting in ["hello", "hi"]):
            return f"Hello! I'm ready to help you. You asked: '{prompt[:30]}...'"
        
        else:
            # General text generation
            words = prompt.split()[-5:]  # Use last 5 words as context
            context = " ".join(words)
            
            responses = [
                f"Based on '{context}', here's my response: This is an interesting topic that deserves careful consideration.",
                f"Regarding '{context}', I think the key points to consider are the following aspects and implications.",
                f"In response to '{context}', let me provide a comprehensive analysis of the situation."
            ]
            
            base_response = responses[hash(prompt) % len(responses)]
            
            # Extend to approximate max_tokens
            words_needed = max(max_tokens - len(base_response.split()), 0)
            extension = " Additional context and details would include relevant information and supporting evidence." * (words_needed // 10 + 1)
            
            return (base_response + extension)[:max_tokens * 6]  # Rough char limit
    
    def _update_performance_stats(self, model_name: str, inference_time: float, tokens: int):
        """Update performance statistics"""
        if model_name not in self.performance_stats:
            self.performance_stats[model_name] = {
                "total_inferences": 0,
                "total_time": 0.0,
                "total_tokens": 0
            }
        
        stats = self.performance_stats[model_name]
        stats["total_inferences"] += 1
        stats["total_time"] += inference_time
        stats["total_tokens"] += tokens
    
    def get_performance_stats(self) -> Dict:
        """Get inference performance statistics"""
        stats = {}
        for model_name, data in self.performance_stats.items():
            if data["total_inferences"] > 0:
                stats[model_name] = {
                    "total_inferences": data["total_inferences"],
                    "avg_inference_time": data["total_time"] / data["total_inferences"],
                    "avg_tokens_per_inference": data["total_tokens"] / data["total_inferences"],
                    "tokens_per_second": data["total_tokens"] / data["total_time"] if data["total_time"] > 0 else 0
                }
        return stats

# Convenience functions for common use cases
class InferenceHelpers:
    def __init__(self, engine: InferenceEngine):
        self.engine = engine
    
    async def quick_generate(self, prompt: str, max_tokens: int = 50) -> str:
        """Quick text generation with minimal configuration"""
        config = InferenceConfig(max_tokens=max_tokens, temperature=0.7)
        result = await self.engine.generate_text(prompt, config)
        
        if result['status'] == 'success':
            return result['generated_text']
        else:
            return f"Error: {result.get('reason', 'Unknown error')}"
    
    async def chat_response(self, message: str) -> str:
        """Generate chat response with optimized settings"""
        config = InferenceConfig(max_tokens=100, temperature=0.8, top_p=0.9)
        result = await self.engine.generate_text(message, config)
        
        if result['status'] == 'success':
            return result['generated_text']
        else:
            return "I'm sorry, I couldn't process your message right now."
    
    async def code_generation(self, description: str) -> str:
        """Generate code with appropriate settings"""
        config = InferenceConfig(max_tokens=200, temperature=0.3, top_p=0.8)
        prompt = f"Generate code for: {description}"
        
        result = await self.engine.generate_text(prompt, config)
        
        if result['status'] == 'success':
            return result['generated_text']
        else:
            return f"# Error generating code: {result.get('reason', 'Unknown error')}"

async def demo_inference_engine():
    """Demonstrate inference engine capabilities"""
    # Import Phase 2 system
    import sys
    sys.path.append('/home/petr/phase2')
    from dynamic_tier_manager import TierManagedServer
    
    model_manager = TierManagedServer()
    engine = InferenceEngine(model_manager)
    helpers = InferenceHelpers(engine)
    
    print("🚀 Phase 3: Inference Engine Demo")
    print("=" * 50)
    
    # Test 1: Quick generation
    print("📝 Quick text generation:")
    result = await helpers.quick_generate("The future of AI is", max_tokens=30)
    print(f"  Result: {result[:100]}...")
    
    # Test 2: Chat response
    print(f"\n💬 Chat response:")
    result = await helpers.chat_response("Hello, how are you today?")
    print(f"  Result: {result[:100]}...")
    
    # Test 3: Code generation
    print(f"\n💻 Code generation:")
    result = await helpers.code_generation("a function that calculates fibonacci numbers")
    print(f"  Result: {result[:150]}...")
    
    # Test 4: Streaming (simulated)
    print(f"\n🌊 Streaming generation:")
    config = InferenceConfig(max_tokens=50, stream=True)
    stream_result = await engine.generate_text("Tell me about machine learning", config)
    print(f"  Stream started: {stream_result.get('stream_id', 'N/A')}")
    
    # Test 5: Performance stats
    print(f"\n📊 Performance statistics:")
    stats = engine.get_performance_stats()
    for model, data in stats.items():
        print(f"  {model}: {data['total_inferences']} inferences, {data['avg_inference_time']:.3f}s avg")

if __name__ == "__main__":
    asyncio.run(demo_inference_engine())
