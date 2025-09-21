# Hot Model Loading API Reference

## Overview
Hot loading allows adding new models to the running system without interruption. Models are loaded in the background and become immediately available once loaded.

## API Endpoints

### 1. Start Hot Loading
```json
{
  "hot_load": {
    "model_name": "my-custom-model",
    "model_config": {
      "size_gb": 2.5,
      "tier": "ram",
      "capabilities": ["text-generation", "chat"]
    }
  }
}
```

**Response:**
```json
{
  "status": "hot_load_started",
  "job_id": "load_my-custom-model_1234567890",
  "model_name": "my-custom-model",
  "estimated_time": "3.8s"
}
```

### 2. Check Loading Status
```json
{
  "load_status": "load_my-custom-model_1234567890"
}
```

**Response:**
```json
{
  "job_id": "load_my-custom-model_1234567890",
  "model_name": "my-custom-model",
  "status": "loading",
  "progress": 0.7,
  "elapsed_time": 2.1,
  "error": null
}
```

### 3. List All Models
```json
{
  "list_models": true
}
```

**Response:**
```json
{
  "status": "success",
  "models": {
    "gpt2-small": {
      "size_gb": 0.5,
      "tier": "ram",
      "capabilities": ["text-generation"]
    },
    "my-custom-model": {
      "size_gb": 2.5,
      "tier": "ram", 
      "capabilities": ["text-generation", "chat"]
    }
  },
  "total_models": 7,
  "active_hot_loads": 0
}
```

## Model Configuration

### Required Fields
- `size_gb`: Model size in gigabytes
- `tier`: Storage tier ("ram" or "swap")
- `capabilities`: List of model capabilities

### Tier Guidelines
- **RAM tier**: ≤3GB, fast access (0.1s per GB load time)
- **Swap tier**: ≤7GB, slower access (0.5s per GB load time)
- **Storage tier**: >7GB, rejected for safety

### Capabilities
- `"text-generation"`: General text generation
- `"text-classification"`: Text classification tasks
- `"chat"`: Conversational AI
- `"code-generation"`: Code generation
- `"embeddings"`: Text embeddings

## Safety Features

### Automatic Validation
- Size limits enforced (max 7GB)
- System capacity checked before loading
- Duplicate model names rejected
- Invalid configurations rejected

### Background Loading
- Non-blocking operation
- Progress tracking
- Error handling and reporting
- Automatic cleanup on failure

## Usage Examples

### Load a Chat Model
```python
# Start loading
response = await server.handle_request({
    "hot_load": {
        "model_name": "chat-assistant",
        "model_config": {
            "size_gb": 1.2,
            "tier": "ram",
            "capabilities": ["text-generation", "chat"]
        }
    }
})

# Monitor progress
job_id = response["job_id"]
while True:
    status = await server.handle_request({"load_status": job_id})
    if status["status"] in ["success", "failed"]:
        break
    await asyncio.sleep(0.5)

# Use the model
result = await server.handle_request({"model": "chat-assistant"})
```

### Load with Quality Priority
```python
# Load large model for quality
await server.handle_request({
    "hot_load": {
        "model_name": "high-quality-model",
        "model_config": {
            "size_gb": 6.5,
            "tier": "swap",
            "capabilities": ["text-generation", "high-quality"]
        }
    }
})
```

## Integration with Phase 2

Hot-loaded models integrate seamlessly with existing Phase 2 features:

- **Intelligent Selection**: Hot-loaded models participate in automatic selection
- **Safety System**: All safety checks apply to hot-loaded models
- **Performance Tracking**: Load times and selection metrics tracked
- **Hot-Swapping**: Can swap between original and hot-loaded models

## Status Values

- `"loading"`: Model is being loaded
- `"success"`: Model loaded successfully and available
- `"failed"`: Loading failed (see error field)

Hot loading extends Phase 2's capabilities while maintaining all existing safety and performance guarantees.
