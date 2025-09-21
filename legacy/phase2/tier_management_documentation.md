# Dynamic Tier Management System

## Overview
The Dynamic Tier Management system allows real-time optimization of model placement between RAM and Swap tiers to balance performance and capacity. Models can be moved between tiers based on usage patterns, performance requirements, or manual optimization.

## Core Concepts

### Storage Tiers
- **RAM Tier**: Fast access (0.1s per GB), limited capacity
- **Swap Tier**: Slower access (0.5s per GB), larger capacity
- **Storage Tier**: Rejected models (>7GB), not loaded

### Tier Operations
- **Promote**: Move model from Swap → RAM (faster access)
- **Demote**: Move model from RAM → Swap (free RAM space)
- **Optimize**: Automatic placement based on usage patterns

## API Reference

### 1. Get Tier Status
```json
{
  "tier_status": true
}
```

**Response:**
```json
{
  "status": "success",
  "tiers": {
    "ram": {
      "used_gb": 4.8,
      "available_gb": 2.6,
      "limit_gb": 5.0,
      "utilization": 0.96,
      "models": 4
    },
    "swap": {
      "used_gb": 13.0,
      "available_gb": 8.0,
      "limit_gb": 10.0,
      "utilization": 1.3,
      "models": 2
    }
  }
}
```

### 2. Move Model Between Tiers
```json
{
  "move_tier": {
    "model_name": "gpt-j-6b",
    "target_tier": "ram"
  }
}
```

**Response:**
```json
{
  "status": "tier_move_started",
  "job_id": "tier_promote_gpt-j-6b_1234567890",
  "model_name": "gpt-j-6b",
  "operation": "promote",
  "source_tier": "swap",
  "target_tier": "ram"
}
```

### 3. Check Tier Move Status
```json
{
  "tier_job_status": "tier_promote_gpt-j-6b_1234567890"
}
```

**Response:**
```json
{
  "job_id": "tier_promote_gpt-j-6b_1234567890",
  "model_name": "gpt-j-6b",
  "operation": "promote",
  "source_tier": "swap",
  "target_tier": "ram",
  "progress": 0.8,
  "status": "running",
  "elapsed_time": 1.2,
  "estimated_time": 1.8,
  "error": null
}
```

### 4. Update Tier Limits
```json
{
  "update_limits": {
    "ram_max_gb": 6.0,
    "swap_max_gb": 12.0,
    "ram_reserved_gb": 1.5
  }
}
```

**Response:**
```json
{
  "status": "success",
  "old_limits": {
    "ram_max_gb": 5.0,
    "swap_max_gb": 10.0,
    "ram_reserved_gb": 1.0
  },
  "new_limits": {
    "ram_max_gb": 6.0,
    "swap_max_gb": 12.0,
    "ram_reserved_gb": 1.5
  }
}
```

### 5. Auto-Optimize Tiers
```json
{
  "auto_optimize": true
}
```

**Response:**
```json
{
  "status": "success",
  "optimizations": [
    "Promoting gpt2-large to RAM (usage: 12)",
    "Promoting bert-large to RAM (usage: 8)"
  ]
}
```

## Configuration Parameters

### Tier Limits
- `ram_max_gb`: Maximum RAM allocation for models (default: 5.0GB)
- `swap_max_gb`: Maximum swap allocation for models (default: 10.0GB)
- `ram_reserved_gb`: RAM reserved for system (default: 1.0GB)

### Safety Constraints
- Minimum RAM limit: 1.0GB
- Minimum swap limit: 2.0GB
- Minimum reserved RAM: 0.5GB
- Maximum single model: 7.0GB

## Performance Impact

### Tier Move Times
- **RAM → Swap**: ~0.2s per GB
- **Swap → RAM**: ~0.3s per GB
- **Background operation**: Non-blocking

### Access Speed Improvement
- **RAM models**: 5x faster loading than swap
- **Immediate effect**: Performance improves after tier move
- **Usage tracking**: System learns from access patterns

## Usage Strategies

### 1. Performance Optimization
```python
# Move frequently used model to RAM
await server.handle_request({
    "move_tier": {
        "model_name": "gpt-j-6b",
        "target_tier": "ram"
    }
})
```

### 2. Capacity Management
```python
# Free RAM by moving large model to swap
await server.handle_request({
    "move_tier": {
        "model_name": "llama-7b", 
        "target_tier": "swap"
    }
})
```

### 3. Dynamic Limits
```python
# Increase RAM allocation for high-performance period
await server.handle_request({
    "update_limits": {
        "ram_max_gb": 6.5
    }
})
```

### 4. Automatic Optimization
```python
# Let system optimize based on usage patterns
await server.handle_request({
    "auto_optimize": true
})
```

## Integration with Existing Features

### Hot Loading
- New models can specify preferred tier
- Automatic tier assignment based on size and capacity
- Hot-loaded models participate in tier optimization

### Intelligent Selection
- Tier placement affects selection scoring
- RAM models preferred for speed priority
- Swap models available for quality priority

### Safety System
- All tier moves validated for safety
- Capacity limits prevent system overload
- Graceful failure with detailed error messages

## Monitoring and Observability

### Key Metrics
- Tier utilization percentages
- Model access frequency
- Tier move success rates
- Performance improvement measurements

### Status Indicators
- `running`: Tier move in progress
- `success`: Tier move completed successfully
- `failed`: Tier move failed (see error field)

## Best Practices

### 1. Monitor Utilization
- Keep RAM utilization below 90%
- Monitor swap usage for performance impact
- Regular tier status checks

### 2. Strategic Placement
- Place frequently used models in RAM
- Use swap for large, occasionally used models
- Consider model size vs. usage frequency

### 3. Capacity Planning
- Reserve adequate RAM for system operations
- Plan tier limits based on workload patterns
- Use auto-optimization for dynamic workloads

### 4. Performance Tuning
- Move critical models to RAM during peak hours
- Use tier moves to prepare for expected workloads
- Monitor tier move completion before using models

## Error Handling

### Common Errors
- `"RAM limit exceeded"`: Increase RAM limit or demote other models
- `"Insufficient RAM"`: Free RAM space or increase limits
- `"Model not found"`: Verify model name spelling
- `"Model already in target tier"`: Check current tier status

### Recovery Strategies
- Check tier status before moves
- Use smaller tier limits initially
- Monitor system resources during moves
- Implement retry logic for failed moves

This tier management system provides fine-grained control over model placement while maintaining all safety and performance guarantees from the Phase 2 system.
