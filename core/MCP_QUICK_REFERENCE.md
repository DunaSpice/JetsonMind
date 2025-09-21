# JetsonMind MCP Quick Reference

## 🚀 Essential Commands

### Text Generation
```json
// Basic generation
{"prompt": "Your question here"}

// Strategic thinking
{"prompt": "Plan a project", "thinking_mode": "strategic"}

// Agent mode (OpenAI compatible)
{"prompt": "Help me code", "agent_mode": true}
```

### Model Management
```json
// List all models
{} // list_models

// Load model to RAM
{"action": "load", "model_name": "llama-7b", "force_tier": "RAM"}

// Check memory usage
{} // get_memory_status

// Hot swap models
{"source_model": "old", "target_model": "new"}
```

### System Monitoring
```json
// System health
{} // get_system_status

// Memory optimization
{"strategy": "balanced"} // optimize_memory

// Model details
{"model_name": "gpt-j-6b"} // get_model_info
```

## 🧠 Thinking Modes
- **immediate**: Fast responses (gpt2-small)
- **strategic**: Deep analysis (gpt-j-6b) 
- **future**: Predictions (gpt-j-6b)

## 💾 Memory Tiers
- **RAM**: 6GB, fastest (gpt2-*, bert-large)
- **SWAP**: 7GB, balanced (gpt-j-6b, llama-7b)
- **STORAGE**: Unlimited, caching

## 🎯 Model Selection Guide
- **gpt2-small**: Quick responses, simple tasks
- **gpt2-medium**: Balanced performance
- **gpt-j-6b**: Complex reasoning, thinking tasks
- **llama-7b**: Agent conversations, instruction following
- **bert-large**: Classification, embeddings

## ⚡ Performance Tips
1. Load frequent models to RAM
2. Use batch_inference for multiple prompts
3. Cache unused models to storage
4. Monitor memory with get_memory_status
5. Optimize with hot_swap_models

## 🔧 Common Patterns

### Development Session
```json
// 1. Load dev model
{"action": "load", "model_name": "llama-7b", "force_tier": "RAM"}

// 2. Create session
{"session_id": "dev_001", "system_prompt": "Expert developer"}

// 3. Strategic coding
{"prompt": "Design API", "thinking_mode": "strategic", "agent_mode": true}
```

### Memory Management
```json
// 1. Check usage
{} // get_memory_status

// 2. Free space
{"action": "unload", "model_name": "unused", "to_storage": true}

// 3. Optimize
{"strategy": "aggressive"}
```

### Batch Processing
```json
// Process multiple prompts
{"prompts": ["Q1", "Q2", "Q3"], "thinking_mode": "immediate"}
```

---
**JetsonMind v4.0 - 10 MCP Tools, 6 Models, 3 Memory Tiers**
