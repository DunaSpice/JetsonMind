# API Reference

## 🔌 API Overview

The Jetson AI System provides multiple API interfaces for different use cases and integration patterns.

## 🎯 MCP Tools (Amazon Q CLI Integration)

### generate
**Purpose**: Text generation with intelligent model selection

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "prompt": {
      "type": "string",
      "description": "Input prompt for text generation"
    }
  },
  "required": ["prompt"]
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "Generated text response"
    },
    "model": {
      "type": "string", 
      "description": "Model used for generation"
    },
    "tokens": {
      "type": "integer",
      "description": "Number of tokens generated"
    },
    "time": {
      "type": "number",
      "description": "Generation time in seconds"
    }
  }
}
```

**Usage Examples**:
```bash
# Basic text generation
q chat "use generate tool with prompt 'Explain quantum computing'"

# Creative writing
q chat "use generate tool with prompt 'Write a short story about AI'"

# Technical documentation
q chat "use generate tool with prompt 'Document this API endpoint'"
```

### get_status
**Purpose**: System health and status monitoring

**Input Schema**: No parameters required

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["operational", "degraded", "error"],
      "description": "Overall system status"
    },
    "uptime": {
      "type": "number",
      "description": "System uptime in seconds"
    },
    "memory": {
      "type": "object",
      "properties": {
        "total": {"type": "number"},
        "used": {"type": "number"},
        "available": {"type": "number"}
      }
    },
    "gpu": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "memory_total": {"type": "number"},
        "memory_used": {"type": "number"},
        "utilization": {"type": "number"}
      }
    },
    "models": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "status": {"type": "string"},
          "memory_usage": {"type": "number"}
        }
      }
    }
  }
}
```

**Usage Examples**:
```bash
# Check system status
q chat "use get_status tool"

# Monitor system health
q chat "use get_status tool" | jq '.memory.available'
```

## 🌐 REST API (Phase 1 Web System)

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
Currently no authentication required for local development. Production deployments should implement proper authentication.

### Endpoints

#### POST /generate
**Purpose**: Generate text using AI models

**Request**:
```json
{
  "prompt": "string",
  "model": "string (optional)",
  "max_tokens": "integer (optional, default: 100)",
  "temperature": "float (optional, default: 0.7)"
}
```

**Response**:
```json
{
  "text": "string",
  "model": "string",
  "tokens": "integer",
  "time": "float",
  "status": "success|error"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, AI!", "max_tokens": 50}'
```

#### GET /status
**Purpose**: Get system status and health information

**Response**:
```json
{
  "status": "operational|degraded|error",
  "uptime": "float",
  "memory": {
    "total": "integer",
    "used": "integer", 
    "available": "integer"
  },
  "gpu": {
    "name": "string",
    "memory_total": "integer",
    "memory_used": "integer",
    "utilization": "float"
  },
  "models": [
    {
      "name": "string",
      "status": "loaded|unloaded|error",
      "memory_usage": "integer"
    }
  ]
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/status
```

#### GET /models
**Purpose**: List available AI models

**Response**:
```json
{
  "models": [
    {
      "name": "string",
      "description": "string",
      "parameters": "integer",
      "status": "available|loaded|error",
      "memory_requirement": "integer"
    }
  ]
}
```

#### POST /models/{model_name}/load
**Purpose**: Load a specific model into memory

**Response**:
```json
{
  "status": "success|error",
  "message": "string",
  "memory_used": "integer",
  "load_time": "float"
}
```

#### POST /models/{model_name}/unload
**Purpose**: Unload a model from memory

**Response**:
```json
{
  "status": "success|error",
  "message": "string",
  "memory_freed": "integer"
}
```

## 🔧 Admin API (Phase 3)

### Base URL
```
http://localhost:8001/admin
```

### Endpoints

#### GET /system/info
**Purpose**: Detailed system information

**Response**:
```json
{
  "hardware": {
    "device": "string",
    "architecture": "string",
    "cpu_cores": "integer",
    "memory_total": "integer",
    "gpu_info": "object"
  },
  "software": {
    "os": "string",
    "python_version": "string",
    "cuda_version": "string",
    "docker_version": "string"
  },
  "services": {
    "mcp_server": "object",
    "web_server": "object",
    "inference_engine": "object"
  }
}
```

#### POST /system/restart
**Purpose**: Restart system components

**Request**:
```json
{
  "component": "mcp_server|web_server|inference_engine|all"
}
```

#### GET /logs
**Purpose**: Retrieve system logs

**Query Parameters**:
- `component`: Filter by component
- `level`: Filter by log level (debug, info, warning, error)
- `limit`: Number of log entries to return

**Response**:
```json
{
  "logs": [
    {
      "timestamp": "string",
      "level": "string",
      "component": "string",
      "message": "string"
    }
  ]
}
```

## 🐍 Python SDK

### Installation
```bash
pip install -r phase3/requirements-mcp.txt
```

### Basic Usage
```python
from inference.inference_engine import InferenceEngine

# Initialize engine
engine = InferenceEngine()

# Generate text
result = engine.generate("Hello, world!")
print(result['text'])

# Get system status
status = engine.get_system_status()
print(f"Status: {status['status']}")
```

### Advanced Usage
```python
from phase3.core_architecture import SystemManager

# Initialize system manager
manager = SystemManager()

# Load specific model
manager.load_model("distilgpt2")

# Generate with specific parameters
result = manager.generate(
    prompt="Explain AI",
    model="distilgpt2",
    max_tokens=100,
    temperature=0.8
)

# Monitor performance
metrics = manager.get_performance_metrics()
```

## 🔍 Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  },
  "timestamp": "string",
  "request_id": "string"
}
```

### Common Error Codes
- `MODEL_NOT_FOUND`: Requested model is not available
- `INSUFFICIENT_MEMORY`: Not enough memory to load model
- `GENERATION_FAILED`: Text generation failed
- `SYSTEM_OVERLOAD`: System is under heavy load
- `INVALID_REQUEST`: Request parameters are invalid

### Error Handling Examples
```python
try:
    result = engine.generate("Hello")
except ModelNotFoundError as e:
    print(f"Model error: {e}")
except InsufficientMemoryError as e:
    print(f"Memory error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 📊 Rate Limiting

### Current Limits
- **MCP Tools**: No explicit limits (controlled by Q CLI)
- **REST API**: 100 requests/minute per IP
- **Admin API**: 10 requests/minute per IP

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 🔐 Security Considerations

### Authentication
- **Development**: No authentication required
- **Production**: Implement API keys or OAuth2

### Input Validation
- All inputs are validated and sanitized
- Maximum prompt length: 2048 characters
- Malicious input detection and blocking

### Resource Protection
- Memory usage monitoring and limits
- Request timeout protection (30 seconds)
- Automatic cleanup of failed operations

---

*This API reference covers all available interfaces for the Jetson AI System. For implementation examples, see the test files in each phase directory.*
