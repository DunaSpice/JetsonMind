# Model Support & Compatibility

## 🤖 Supported Models

### ✅ Verified Working Models

| Model | Parameters | Memory Usage | Performance | Container | Status |
|-------|------------|--------------|-------------|-----------|--------|
| **DistilGPT-2** | 82M | ~1.5GB | Excellent | dustynv/mlc:r36.4.0 | ✅ Production Ready |
| **DialoGPT-small** | 117M | ~2GB | Excellent | dustynv/mlc:r36.4.0 | ✅ Production Ready |
| **GPT-2** | 124M | ~2.5GB | Excellent | dustynv/mlc:r36.4.0 | ✅ Production Ready |

### ❌ Known Incompatible Models

| Model | Parameters | Issue | Container | Notes |
|-------|------------|-------|-----------|-------|
| **SmolLM2-135M** | 135M | MLC Quantization Crash | dustynv/nano_llm:r36.2.0 | Filesystem/quantization issues |
| **Qwen2.5-0.5B** | 500M | MLC Quantization Crash | dustynv/nano_llm:r36.2.0 | Same quantization problems |

## 🎯 Model Categories

### Text Generation Models
**Best for**: Creative writing, content generation, general text tasks

- **DistilGPT-2**: Lightweight, fast, good for general text generation
- **GPT-2**: More capable, slightly slower, better quality output
- **DialoGPT-small**: Optimized for conversational AI

### Conversational Models  
**Best for**: Chatbots, Q&A systems, interactive applications

- **DialoGPT-small**: Specifically trained for dialogue
- **GPT-2**: Can be adapted for conversation with proper prompting

### Specialized Models
**Future Support**: Models for specific domains

- **Code Generation**: CodeT5, CodeBERT (planned)
- **Summarization**: BART, T5 (planned)
- **Translation**: mBART, M2M-100 (planned)

## 🔧 Model Integration Guide

### Adding New Models

1. **Test Compatibility**
```python
from inference.inference_engine import InferenceEngine

engine = InferenceEngine()
try:
    engine.load_model("new-model-name")
    result = engine.generate("test prompt")
    print("Model compatible!")
except Exception as e:
    print(f"Compatibility issue: {e}")
```

2. **Memory Requirements**
```python
# Check memory before loading
def check_model_compatibility(model_name):
    required_memory = estimate_model_memory(model_name)
    available_memory = get_available_memory()
    
    if required_memory > available_memory:
        return False, f"Need {required_memory}MB, have {available_memory}MB"
    
    return True, "Compatible"
```

3. **Performance Testing**
```bash
# Run performance benchmarks
cd phase3
python3 test_comprehensive.py --model new-model-name
```

### Model Configuration

**Model Registry** (`models.json`):
```json
{
  "models": {
    "distilgpt2": {
      "name": "DistilGPT-2",
      "parameters": "82M",
      "memory_requirement": 1500,
      "container": "dustynv/mlc:r36.4.0",
      "status": "production",
      "use_cases": ["text_generation", "creative_writing"]
    }
  }
}
```

## 📊 Performance Characteristics

### Memory Usage Patterns
```
Small Models (80-130M):   1.5-2.5GB RAM
Medium Models (300-500M): 3-5GB RAM  
Large Models (1B+):       6-8GB RAM (near limit)
```

### Inference Speed
```
DistilGPT-2:    25-45 tokens/second
DialoGPT-small: 20-35 tokens/second  
GPT-2:          15-30 tokens/second
```

### Loading Times
```
Small Models:  2-5 seconds
Medium Models: 5-10 seconds
Large Models:  10-20 seconds
```

## 🚀 Optimization Strategies

### Memory Optimization
1. **Float16 Precision**: Reduces memory usage by ~50%
2. **Model Quantization**: 8-bit quantization when supported
3. **Dynamic Loading**: Load models on-demand
4. **Memory Pooling**: Reuse memory buffers

### Performance Optimization
1. **Batch Processing**: Process multiple requests together
2. **Caching**: Cache frequent model outputs
3. **GPU Acceleration**: Leverage CUDA when available
4. **Model Compilation**: Pre-compile models for faster inference

## 🔍 Model Selection Logic

### Automatic Model Selection
The inference engine automatically selects models based on:

1. **Task Type Detection**
```python
def select_model_for_task(prompt):
    if is_conversational(prompt):
        return "dialogpt-small"
    elif is_creative_writing(prompt):
        return "gpt2"
    else:
        return "distilgpt2"  # Default
```

2. **Resource Availability**
```python
def select_model_by_resources():
    available_memory = get_available_memory()
    
    if available_memory > 4000:
        return "gpt2"
    elif available_memory > 2500:
        return "dialogpt-small"
    else:
        return "distilgpt2"
```

3. **Performance Requirements**
```python
def select_model_by_performance(speed_priority=False):
    if speed_priority:
        return "distilgpt2"  # Fastest
    else:
        return "gpt2"  # Best quality
```

## 🧪 Testing New Models

### Compatibility Checklist
- [ ] Model loads without errors
- [ ] Memory usage within limits (<6GB)
- [ ] Generates coherent text
- [ ] Performance acceptable (>10 tokens/sec)
- [ ] No memory leaks over time
- [ ] Compatible with container environment

### Test Script
```python
#!/usr/bin/env python3
"""Test script for new model compatibility"""

import time
import psutil
from inference.inference_engine import InferenceEngine

def test_model_compatibility(model_name):
    engine = InferenceEngine()
    
    # Test 1: Loading
    print(f"Testing {model_name}...")
    start_time = time.time()
    try:
        engine.load_model(model_name)
        load_time = time.time() - start_time
        print(f"✅ Loaded in {load_time:.2f}s")
    except Exception as e:
        print(f"❌ Load failed: {e}")
        return False
    
    # Test 2: Memory usage
    memory_usage = psutil.virtual_memory().used / 1024**3
    print(f"Memory usage: {memory_usage:.2f}GB")
    
    # Test 3: Generation
    try:
        result = engine.generate("Hello, world!")
        print(f"✅ Generated: {result['text'][:50]}...")
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False
    
    # Test 4: Performance
    start_time = time.time()
    result = engine.generate("Test prompt for performance measurement")
    generation_time = time.time() - start_time
    tokens_per_second = len(result['text'].split()) / generation_time
    print(f"Performance: {tokens_per_second:.1f} tokens/second")
    
    return True

if __name__ == "__main__":
    test_model_compatibility("new-model-name")
```

## 🔮 Future Model Support

### Planned Additions
1. **Larger Models**: Support for 1B+ parameter models with optimization
2. **Multimodal Models**: Vision-language models (VLM)
3. **Specialized Models**: Code generation, summarization, translation
4. **Custom Models**: Support for user fine-tuned models

### Research Areas
1. **Model Compression**: Advanced quantization techniques
2. **Distributed Inference**: Multi-device model execution
3. **Dynamic Batching**: Improved throughput optimization
4. **Model Caching**: Intelligent model swapping strategies

---

*This model support guide is continuously updated as new models are tested and validated on the Jetson platform.*
