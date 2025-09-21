# Troubleshooting Guide

## 🚨 Common Issues & Solutions

### MCP Server Issues

#### Issue: MCP Server Won't Start
**Error**: `'function' object is not subscriptable`

**Solution**:
```bash
# Check virtual environment
cd /home/petr/jetson/phase3
source mcp_env/bin/activate
which python3

# Verify MCP installation
pip list | grep mcp

# Restart with debug
export DEBUG=1
python3 mcp_server_minimal.py
```

#### Issue: Connection Closed During Initialization
**Error**: `connection closed: initialize response`

**Solution**:
```bash
# Check MCP configuration
cat ~/.aws/amazonq/mcp.json

# Verify wrapper script permissions
chmod +x mcp_wrapper.sh

# Test wrapper directly
./mcp_wrapper.sh

# Recreate MCP configuration
./setup.sh
```

#### Issue: Tool Not Found
**Error**: `Tool 'generate' not found`

**Solution**:
```bash
# Verify tool registration
q chat "list available tools"

# Check MCP server logs
tail -f ~/.aws/amazonq/logs/mcp.log

# Restart Q CLI
q quit
q chat "use get_status tool"
```

### Memory Issues

#### Issue: Out of Memory Error
**Error**: `CUDA out of memory` or `RuntimeError: out of memory`

**Solution**:
```bash
# Check memory usage
nvidia-smi
htop

# Free GPU memory
python3 -c "
import torch
torch.cuda.empty_cache()
print('GPU memory cleared')
"

# Restart with smaller model
q chat "use generate tool with prompt 'test' --model distilgpt2"
```

#### Issue: Memory Leaks
**Symptoms**: Gradually increasing memory usage

**Solution**:
```python
# Add explicit cleanup
import gc
import torch

def cleanup_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# Call after each inference
cleanup_memory()
```

### Model Loading Issues

#### Issue: Model Not Found
**Error**: `Model 'model-name' not found`

**Solution**:
```bash
# Check available models
python3 -c "
from inference.inference_engine import InferenceEngine
engine = InferenceEngine()
print(engine.list_available_models())
"

# Download model manually
python3 -c "
from transformers import AutoModel, AutoTokenizer
model = AutoModel.from_pretrained('distilgpt2')
tokenizer = AutoTokenizer.from_pretrained('distilgpt2')
"
```

#### Issue: Model Loading Timeout
**Error**: `TimeoutError: Model loading exceeded 30 seconds`

**Solution**:
```bash
# Increase timeout
export MODEL_LOAD_TIMEOUT=120

# Pre-download models
python3 -c "
from transformers import AutoModel
models = ['distilgpt2', 'microsoft/DialoGPT-small']
for model in models:
    AutoModel.from_pretrained(model)
"
```

### Container Issues

#### Issue: CUDA Not Available
**Error**: `CUDA is not available`

**Solution**:
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Verify container GPU access
docker run --rm --gpus all dustynv/mlc:r36.4.0 nvidia-smi

# Restart Docker with NVIDIA runtime
sudo systemctl restart docker
```

#### Issue: Container Won't Start
**Error**: `Container failed to start`

**Solution**:
```bash
# Check container logs
docker logs <container-id>

# Verify image exists
docker images | grep dustynv

# Pull latest image
docker pull dustynv/mlc:r36.4.0

# Check disk space
df -h
```

### Performance Issues

#### Issue: Slow Inference
**Symptoms**: Generation takes >10 seconds

**Solution**:
```bash
# Check GPU utilization
nvidia-smi -l 1

# Monitor CPU usage
htop

# Use smaller model
q chat "use generate tool with prompt 'test' --model distilgpt2"

# Enable GPU acceleration
export CUDA_VISIBLE_DEVICES=0
```

#### Issue: High Memory Usage
**Symptoms**: System becomes unresponsive

**Solution**:
```bash
# Monitor memory usage
watch -n 1 'free -h && nvidia-smi'

# Reduce batch size
export BATCH_SIZE=1

# Use memory-efficient models
export PREFER_SMALL_MODELS=true
```

### Network Issues

#### Issue: Model Download Fails
**Error**: `Connection timeout` or `HTTP 403`

**Solution**:
```bash
# Check internet connection
ping huggingface.co

# Use different mirror
export HF_ENDPOINT=https://hf-mirror.com

# Download manually
wget https://huggingface.co/distilgpt2/resolve/main/config.json
```

#### Issue: API Endpoint Not Responding
**Error**: `Connection refused` on localhost:8000

**Solution**:
```bash
# Check if server is running
ps aux | grep python

# Check port availability
netstat -tlnp | grep 8000

# Restart server
cd phase3
./run_admin_server.sh

# Check firewall
sudo ufw status
```

## 🔧 Diagnostic Commands

### System Health Check
```bash
#!/bin/bash
echo "=== System Health Check ==="

echo "1. Hardware Info:"
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv

echo "2. Memory Usage:"
free -h

echo "3. Disk Space:"
df -h /

echo "4. Docker Status:"
docker ps

echo "5. Python Environment:"
which python3
python3 --version

echo "6. MCP Configuration:"
cat ~/.aws/amazonq/mcp.json

echo "7. Process Status:"
ps aux | grep -E "(mcp|python|docker)"
```

### Performance Diagnostics
```bash
#!/bin/bash
echo "=== Performance Diagnostics ==="

echo "1. GPU Performance:"
nvidia-smi dmon -c 10

echo "2. CPU Performance:"
top -b -n 1 | head -20

echo "3. Memory Performance:"
vmstat 1 5

echo "4. Disk I/O:"
iostat -x 1 5

echo "5. Network:"
netstat -i
```

### Log Analysis
```bash
#!/bin/bash
echo "=== Log Analysis ==="

echo "1. System Logs:"
journalctl -u docker --since "1 hour ago" | tail -20

echo "2. Application Logs:"
tail -50 /home/petr/jetson/phase3/api_bridge.log

echo "3. MCP Logs:"
tail -50 ~/.aws/amazonq/logs/mcp.log

echo "4. Docker Logs:"
docker logs $(docker ps -q) --tail 20
```

## 🛠️ Recovery Procedures

### Complete System Reset
```bash
#!/bin/bash
echo "Performing complete system reset..."

# Stop all services
docker stop $(docker ps -q)
pkill -f mcp_server

# Clean up resources
docker system prune -f
python3 -c "import torch; torch.cuda.empty_cache()"

# Restart services
cd /home/petr/jetson/phase3
./setup.sh

echo "System reset complete"
```

### Emergency Recovery
```bash
#!/bin/bash
echo "Emergency recovery procedure..."

# Kill all Python processes
pkill -f python3

# Clear GPU memory
nvidia-smi --gpu-reset

# Restart Docker
sudo systemctl restart docker

# Reboot if necessary
# sudo reboot
```

## 📞 Getting Help

### Debug Information to Collect
When reporting issues, include:

1. **System Information**:
```bash
uname -a
nvidia-smi
free -h
df -h
```

2. **Software Versions**:
```bash
python3 --version
docker --version
pip list | grep -E "(torch|transformers|mcp)"
```

3. **Error Logs**:
```bash
tail -100 ~/.aws/amazonq/logs/mcp.log
tail -100 /home/petr/jetson/phase3/api_bridge.log
```

4. **Configuration**:
```bash
cat ~/.aws/amazonq/mcp.json
cat /home/petr/jetson/phase3/mcp_config.json
```

### Support Channels
- **Documentation**: Check this troubleshooting guide first
- **GitHub Issues**: Create detailed issue reports
- **Community Forums**: NVIDIA Developer Forums for Jetson-specific issues
- **Stack Overflow**: For general Python/PyTorch questions

---

*This troubleshooting guide covers the most common issues encountered during development and deployment. Keep it updated as new issues are discovered and resolved.*
