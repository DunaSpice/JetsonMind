# Jetson Orin Nano - Model Installation Commands

## Prerequisites
```bash
# Ensure Docker is installed and running
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (logout/login required)
sudo usermod -aG docker $USER
```

## Language Models (LLM) Installation

### Small Models (Recommended for Orin Nano)
```bash
# SmolLM2 135M - Smallest model
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_llm:r36.2.0

# SmolLM2 360M
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_llm:r36.2.0

# Llama 3.2 1B
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_llm:r36.2.0

# Qwen 2.5 0.5B
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_llm:r36.2.0
```

### Medium Models (Good performance on Orin Nano)
```bash
# Llama 3.2 3B
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_llm:r36.2.0

# Qwen 2.5 3B
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_llm:r36.2.0

# Gemma 2 2B
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_llm:r36.2.0
```

### Larger Models (May require optimization)
```bash
# Qwen 2.5 7B
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_llm:r36.2.0

# Llama 3.1 8B
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_llm:r36.2.0
```

## Vision/Language Models (VLM) Installation

### Recommended VLM Models for Orin Nano
```bash
# LLaVA 1.5 7B
sudo docker run --runtime nvidia -it --rm --network=host dustynv/llava:r36.2.0

# Qwen 2.5 VL 3B
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_vlm:r36.2.0

# Phi 3.5 Vision
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_vlm:r36.2.0
```

## Web UI Applications

### Open WebUI (Recommended interface)
```bash
sudo docker run --runtime nvidia -it --rm --network=host dustynv/open-webui:r36.2.0
```

### Text Generation WebUI
```bash
sudo docker run --runtime nvidia -it --rm --network=host dustynv/text-generation-webui:r36.2.0
```

### Ollama
```bash
sudo docker run --runtime nvidia -it --rm --network=host dustynv/ollama:r36.2.0
```

## Quick Start Commands

### Start a basic LLM server
```bash
# Start NanoLLM with default model
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_llm:r36.2.0 \
  python3 -m nano_llm.chat --api=mlc --model=Qwen/Qwen2.5-0.5B-Instruct
```

### Start a VLM server
```bash
# Start NanoVLM with LLaVA
sudo docker run --runtime nvidia -it --rm --network=host dustynv/nano_vlm:r36.2.0 \
  python3 -m nano_llm.vision --model=llava-v1.5-7b
```

### Start Open WebUI
```bash
sudo docker run --runtime nvidia -it --rm --network=host dustynv/open-webui:r36.2.0
# Access via http://localhost:8080
```

## Performance Tips for Orin Nano

### Memory Optimization
```bash
# Increase swap space
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Docker Optimization
```bash
# Set Docker to use all available GPU memory
export CUDA_VISIBLE_DEVICES=0
export NVIDIA_VISIBLE_DEVICES=all
```

### Model Selection Guidelines
- **For basic text generation**: SmolLM2 135M/360M, Qwen 2.5 0.5B
- **For better quality**: Llama 3.2 1B/3B, Qwen 2.5 1.5B/3B
- **For vision tasks**: LLaVA 1.5 7B, Qwen 2.5 VL 3B
- **For development**: Open WebUI + smaller models

## Troubleshooting
```bash
# Check GPU status
nvidia-smi

# Check Docker GPU runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Monitor system resources
htop
watch -n 1 nvidia-smi
```

## Notes
- All commands assume JetPack 5.1+ with Docker runtime support
- Models will be downloaded on first run (may take time)
- Adjust model parameters based on available memory
- Use quantized models for better performance on Orin Nano
