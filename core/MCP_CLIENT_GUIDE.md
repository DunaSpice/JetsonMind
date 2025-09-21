# JetsonMind MCP Client Guide

## Overview
JetsonMind provides a comprehensive AI inference system through MCP (Model Context Protocol). This guide explains all available tools and how to use them effectively.

## 🚀 Quick Start

**Connect to JetsonMind MCP Server:**
```bash
# Server runs on: /home/petr/jetson/core/run_mcp_server.sh
# Available through Q CLI or any MCP-compatible client
```

## 📋 Available Tools (10 Total)

### 1. `generate_text` - Advanced Text Generation
**Purpose:** Generate text with thinking modes and intelligent model selection

**Parameters:**
- `prompt` (required): Input text prompt
- `thinking_mode` (optional): "immediate", "future", "strategic" 
- `agent_mode` (optional): true/false for OpenAI compatibility
- `model` (optional): Specific model name
- `max_tokens` (optional): Maximum response length (default: 100)
- `temperature` (optional): Creativity level 0.0-1.0 (default: 0.7)

**Examples:**
```json
// Quick response
{"prompt": "Hello world"}

// Strategic thinking for planning
{"prompt": "Plan a software project", "thinking_mode": "strategic"}

// Future-focused analysis
{"prompt": "What will AI look like in 2030?", "thinking_mode": "future"}

// OpenAI agent compatibility
{"prompt": "Help me debug code", "agent_mode": true}

// Force specific model
{"prompt": "Analyze this data", "model": "llama-7b"}
```

**Response Format:**
```json
{
  "text": "Generated response text",
  "model": "selected_model_name",
  "thinking_mode": "strategic",
  "generation_time": 0.15,
  "tokens": 25
}
```

### 2. `list_models` - Model Library
**Purpose:** Get all available models with capabilities

**Parameters:** None

**Response:**
```json
{
  "gpt2-small": {
    "size_gb": 0.5,
    "tier": "ram",
    "capabilities": ["text-generation", "fast"],
    "thinking_capable": false
  },
  "llama-7b": {
    "size_gb": 7.0,
    "tier": "swap", 
    "capabilities": ["instruction-following", "reasoning"],
    "thinking_capable": true
  }
}
```

### 3. `get_model_info` - Detailed Model Information
**Purpose:** Get comprehensive info about a specific model

**Parameters:**
- `model_name` (required): Name of model to query

**Example:**
```json
{"model_name": "gpt-j-6b"}
```

**Response:**
```json
{
  "name": "gpt-j-6b",
  "size_gb": 6.0,
  "tier": "swap",
  "capabilities": ["text-generation", "high-quality"],
  "thinking_capable": true,
  "loaded": false
}
```

### 4. `select_optimal_model` - AI Model Recommendation
**Purpose:** Get AI-powered model recommendation for your task

**Parameters:**
- `prompt` (required): Your task description
- `thinking_mode` (optional): Thinking approach needed
- `agent_mode` (optional): Agent compatibility required

**Example:**
```json
{
  "prompt": "Complex reasoning task requiring deep analysis",
  "thinking_mode": "strategic"
}
```

**Response:**
```json
{
  "recommended_model": "gpt-j-6b",
  "reasoning": "Selected based on prompt complexity and thinking requirements",
  "model_info": {
    "size_gb": 6.0,
    "tier": "swap",
    "capabilities": ["text-generation", "high-quality"]
  }
}
```

### 5. `manage_model_loading` - Hot Model Management
**Purpose:** Load/unload models with memory tier control

**Parameters:**
- `action` (required): "load", "unload", "status", "hot_swap"
- `model_name` (optional): Model to manage
- `force_tier` (optional): "RAM", "SWAP", "STORAGE"
- `to_storage` (optional): Cache to storage when unloading

**Examples:**
```json
// Check loading status
{"action": "status"}

// Load model to specific tier
{"action": "load", "model_name": "llama-7b", "force_tier": "RAM"}

// Unload and cache to storage
{"action": "unload", "model_name": "gpt2-large", "to_storage": true}

// Hot swap (unload current, prepare for new)
{"action": "hot_swap", "model_name": "gpt2-small"}
```

**Load Response:**
```json
{
  "status": "loaded",
  "model": "llama-7b",
  "location": "RAM",
  "size_gb": 7.0,
  "load_time": 0.1
}
```

### 6. `get_memory_status` - Memory Monitoring
**Purpose:** Real-time memory usage across all tiers

**Parameters:** None

**Response:**
```json
{
  "system": {
    "ram_total_gb": 7.5,
    "ram_available_gb": 2.1,
    "swap_total_gb": 12.0,
    "swap_used_gb": 3.2
  },
  "jetsonmind": {
    "ram_limit_gb": 6.0,
    "swap_limit_gb": 7.0,
    "ram_used_gb": 1.5,
    "swap_used_gb": 6.0,
    "loaded_models": {
      "gpt2-small": {"location": "RAM", "size_gb": 0.5},
      "gpt-j-6b": {"location": "SWAP", "size_gb": 6.0}
    }
  }
}
```

### 7. `hot_swap_models` - Instant Model Swapping
**Purpose:** Swap models for optimal performance

**Parameters:**
- `source_model` (required): Model to swap out
- `target_model` (required): Model to swap in
- `target_tier` (optional): Preferred memory tier

**Example:**
```json
{
  "source_model": "gpt2-small",
  "target_model": "bert-large",
  "target_tier": "RAM"
}
```

**Response:**
```json
{
  "hot_swap_completed": true,
  "unloaded": {"status": "unloaded", "cached_to_storage": true},
  "loaded": {"status": "loaded", "location": "RAM"}
}
```

### 8. `batch_inference` - Multi-Prompt Processing
**Purpose:** Process multiple prompts efficiently

**Parameters:**
- `prompts` (required): Array of text prompts
- `thinking_mode` (optional): Mode for all prompts
- `model` (optional): Model for all prompts

**Example:**
```json
{
  "prompts": ["Hello", "How are you?", "Goodbye"],
  "thinking_mode": "immediate"
}
```

**Response:**
```json
{
  "batch_results": [
    {"text": "Response 1", "model": "gpt2-small"},
    {"text": "Response 2", "model": "gpt2-small"},
    {"text": "Response 3", "model": "gpt2-small"}
  ],
  "total_processed": 3
}
```

### 9. `create_agent_session` - Persistent Conversations
**Purpose:** Create multi-turn conversation sessions

**Parameters:**
- `session_id` (required): Unique session identifier
- `model` (optional): Model for session (default: "llama-7b")
- `system_prompt` (optional): System instructions

**Example:**
```json
{
  "session_id": "coding_assistant_001",
  "model": "llama-7b",
  "system_prompt": "You are an expert Python developer."
}
```

### 10. `get_system_status` - Health Monitoring
**Purpose:** Overall system health and capabilities

**Parameters:** None

**Response:**
```json
{
  "status": "healthy",
  "models_available": 6,
  "models_loaded": 2,
  "thinking_modes": ["immediate", "future", "strategic"],
  "agent_compatible": true,
  "version": "4.0.0"
}
```

## 🧠 Understanding Thinking Modes

### Immediate Mode (Default)
- **Use for:** Quick responses, simple questions
- **Model selection:** Fast, lightweight models (gpt2-small)
- **Response time:** Fastest

### Strategic Mode
- **Use for:** Planning, analysis, complex reasoning
- **Model selection:** Thinking-capable models (gpt-j-6b, llama-7b)
- **Response format:** Structured analysis with [STRATEGIC ANALYSIS] prefix

### Future Mode
- **Use for:** Predictions, long-term planning, trend analysis
- **Model selection:** Thinking-capable models
- **Response format:** Forward-looking with [FUTURE THINKING] prefix

## 💾 Memory Tier System

### RAM Tier (Fastest)
- **Capacity:** ~6GB (80% of system RAM)
- **Best for:** Frequently used models, real-time inference
- **Models:** gpt2-small, gpt2-medium, bert-large

### SWAP Tier (Balanced)
- **Capacity:** ~7GB (60% of system swap)
- **Best for:** Larger models, occasional use
- **Models:** gpt-j-6b, llama-7b

### STORAGE Tier (Unlimited)
- **Capacity:** Disk-based (unlimited)
- **Best for:** Model caching, cold storage
- **Use case:** Hot swapping, memory optimization

## 🎯 Best Practices

### For Performance
1. **Load frequently used models to RAM tier**
2. **Use immediate mode for simple tasks**
3. **Batch similar prompts together**
4. **Monitor memory usage regularly**

### For Quality
1. **Use strategic mode for complex reasoning**
2. **Choose thinking-capable models for analysis**
3. **Create agent sessions for multi-turn conversations**
4. **Use future mode for predictions**

### For Memory Management
1. **Check memory status before loading large models**
2. **Use hot swapping for dynamic workloads**
3. **Cache unused models to storage**
4. **Run memory optimization periodically**

## 🔧 Troubleshooting

### Model Loading Issues
```json
// Check what's loaded
{"action": "status"}

// Free memory if needed
{"strategy": "aggressive"}

// Force load to specific tier
{"action": "load", "model_name": "model", "force_tier": "SWAP"}
```

### Performance Issues
```json
// Check system status
{}  // get_system_status

// Optimize memory
{"strategy": "balanced"}

// Move model to faster tier
{"action": "load", "model_name": "model", "force_tier": "RAM"}
```

### Memory Errors
```json
// Check memory usage
{}  // get_memory_status

// Free up space
{"action": "unload", "model_name": "unused_model", "to_storage": true}

// Optimize automatically
{"strategy": "aggressive"}
```

## 📊 Example Workflows

### Development Workflow
```json
// 1. Check system status
{"tool": "get_system_status"}

// 2. Load development model
{"tool": "manage_model_loading", "action": "load", "model_name": "llama-7b", "force_tier": "RAM"}

// 3. Create coding session
{"tool": "create_agent_session", "session_id": "dev_001", "system_prompt": "Expert developer"}

// 4. Generate code with strategic thinking
{"tool": "generate_text", "prompt": "Design a REST API", "thinking_mode": "strategic", "agent_mode": true}
```

### Analysis Workflow
```json
// 1. Load analysis model
{"tool": "manage_model_loading", "action": "load", "model_name": "gpt-j-6b"}

// 2. Batch analyze data
{"tool": "batch_inference", "prompts": ["Analyze trend 1", "Analyze trend 2"], "thinking_mode": "strategic"}

// 3. Future predictions
{"tool": "generate_text", "prompt": "What will happen next?", "thinking_mode": "future"}
```

### Memory Optimization Workflow
```json
// 1. Check current usage
{"tool": "get_memory_status"}

// 2. Optimize memory
{"tool": "optimize_memory", "strategy": "balanced"}

// 3. Hot swap models
{"tool": "hot_swap_models", "source_model": "old_model", "target_model": "new_model", "target_tier": "RAM"}
```

---

**JetsonMind MCP Server - Complete AI Platform for Edge Devices**  
*Version 4.0.0 - Advanced Model Management with Hot Loading*
