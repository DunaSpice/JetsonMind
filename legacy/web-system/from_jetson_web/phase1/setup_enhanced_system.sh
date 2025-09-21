#!/bin/bash

echo "🚀 Setting up Enhanced Jetson AI Server System"
echo "=============================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "📚 Installing required packages..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers
pip install fastapi uvicorn
pip install psutil
pip install numpy
pip install pydantic
pip install asyncio-mqtt  # For future MQTT integration
pip install prometheus-client  # For metrics export
pip install aiofiles  # For async file operations

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /tmp/model_swap
mkdir -p logs
mkdir -p configs
mkdir -p data

# Set permissions
chmod +x enhanced_model_server.py
chmod +x performance_optimizer.py  
chmod +x api_server.py

# Create systemd service file
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/jetson-ai-server.service > /dev/null <<EOF
[Unit]
Description=Enhanced Jetson AI Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python api_server.py --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create configuration file
echo "⚙️ Creating configuration..."
cat > configs/server_config.json <<EOF
{
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 1
    },
    "memory": {
        "ram_budget_gb": 5.5,
        "swap_dir": "/tmp/model_swap",
        "optimization_interval": 60
    },
    "models": {
        "preload": [
            "Qwen/Qwen2.5-0.5B-Instruct",
            "Qwen/Qwen2.5-1.5B-Instruct"
        ],
        "model_capabilities": {
            "Qwen/Qwen2.5-0.5B-Instruct": ["general", "chat", "simple"],
            "Qwen/Qwen2.5-1.5B-Instruct": ["coding", "analysis", "medium"],
            "Qwen/Qwen2.5-3B-Instruct": ["complex", "reasoning", "large"]
        }
    },
    "monitoring": {
        "metrics_history_size": 1000,
        "alert_thresholds": {
            "ram_percent": 90,
            "cpu_temp": 80,
            "gpu_temp": 85,
            "cpu_percent": 95
        }
    },
    "optimization": {
        "aggressive_threshold": 0.8,
        "moderate_threshold": 0.6,
        "preload_threshold": 0.9
    }
}
EOF

# Create startup script
echo "🎬 Creating startup script..."
cat > start_server.sh <<EOF
#!/bin/bash
cd "$(dirname "\$0")"
source venv/bin/activate

echo "🚀 Starting Enhanced Jetson AI Server..."
echo "📊 System Info:"
echo "  RAM: \$(free -h | grep Mem | awk '{print \$3 "/" \$2}')"
echo "  Swap: \$(free -h | grep Swap | awk '{print \$3 "/" \$2}')"
echo "  GPU: \$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{print \$1 "MB/" \$2 "MB"}')"
echo "  Temp: \$(cat /sys/class/thermal/thermal_zone0/temp | awk '{print \$1/1000 "°C"}')"
echo ""

python api_server.py --host 0.0.0.0 --port 8000
EOF

chmod +x start_server.sh

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > monitor_system.py <<EOF
#!/usr/bin/env python3
import requests
import time
import json

def monitor_server():
    base_url = "http://localhost:8000"
    
    while True:
        try:
            # Get status
            status = requests.get(f"{base_url}/status").json()
            
            print(f"\\n📊 System Status - {time.strftime('%H:%M:%S')}")
            print(f"  Active Models: {len(status['active_models'])}")
            print(f"  Memory: {status['memory_usage_gb']:.1f}GB / {status['memory_budget_gb']:.1f}GB")
            print(f"  CPU: {status['cpu_percent']:.1f}%")
            print(f"  GPU Memory: {status['gpu_memory_gb']:.1f}GB")
            print(f"  Temperature: {status['temperature_c']:.1f}°C")
            print(f"  Queue Size: {status['queue_size']}")
            
            if status['alerts']:
                print(f"  🚨 Alerts: {len(status['alerts'])}")
                for alert in status['alerts'][-3:]:
                    print(f"    - {alert['type']}: {alert['message']}")
            
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
        
        time.sleep(10)

if __name__ == "__main__":
    monitor_server()
EOF

chmod +x monitor_system.py

# Create test script
echo "🧪 Creating test script..."
cat > test_server.py <<EOF
#!/usr/bin/env python3
import requests
import json
import time
import asyncio

async def test_server():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Enhanced AI Server")
    print("=" * 40)
    
    # Test health
    print("1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   ✅ Health: {response.json()['status']}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test status
    print("2. System Status...")
    try:
        response = requests.get(f"{base_url}/status")
        status = response.json()
        print(f"   ✅ Active models: {len(status['active_models'])}")
        print(f"   ✅ Memory usage: {status['memory_usage_gb']:.1f}GB")
    except Exception as e:
        print(f"   ❌ Status check failed: {e}")
    
    # Test inference
    print("3. Single Inference...")
    try:
        test_request = {
            "prompt": "What is artificial intelligence?",
            "max_length": 30
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/inference", json=test_request)
        inference_time = time.time() - start_time
        
        result = response.json()
        print(f"   ✅ Response: {result['response'][:50]}...")
        print(f"   ✅ Model: {result['model_used']}")
        print(f"   ✅ Speed: {result['tokens_per_second']:.1f} tok/s")
        print(f"   ✅ Total time: {inference_time:.2f}s")
        
    except Exception as e:
        print(f"   ❌ Inference test failed: {e}")
    
    # Test batch inference
    print("4. Batch Inference...")
    try:
        batch_request = {
            "prompts": [
                "Hello, how are you?",
                "What is 2+2?",
                "Tell me a joke"
            ]
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/batch_inference", json=batch_request)
        batch_time = time.time() - start_time
        
        result = response.json()
        print(f"   ✅ Batch size: {result['batch_size']}")
        print(f"   ✅ Total time: {batch_time:.2f}s")
        print(f"   ✅ Avg per request: {result['avg_time_per_request']:.2f}s")
        
    except Exception as e:
        print(f"   ❌ Batch test failed: {e}")
    
    # Test performance endpoint
    print("5. Performance Analytics...")
    try:
        response = requests.get(f"{base_url}/performance")
        perf = response.json()
        
        if perf['system_report']['total_models_tested'] > 0:
            best_model = perf['system_report']['best_performing_model']
            print(f"   ✅ Best model: {best_model[0] if best_model else 'None'}")
        
        recent = perf['recent_performance']
        if recent:
            print(f"   ✅ Avg RAM: {recent.get('avg_ram_percent', 0):.1f}%")
            print(f"   ✅ Avg CPU: {recent.get('avg_cpu_percent', 0):.1f}%")
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
    
    print("\\n🎉 Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_server())
EOF

chmod +x test_server.py

# Create Docker setup (optional)
echo "🐳 Creating Docker setup..."
cat > Dockerfile <<EOF
FROM nvcr.io/nvidia/l4t-pytorch:r35.2.1-pth2.0-py3

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    python3-pip \\
    python3-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Create swap directory
RUN mkdir -p /tmp/model_swap

# Expose port
EXPOSE 8000

# Run the server
CMD ["python3", "api_server.py", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create requirements.txt
cat > requirements.txt <<EOF
torch>=2.0.0
transformers>=4.30.0
fastapi>=0.100.0
uvicorn>=0.22.0
psutil>=5.9.0
numpy>=1.24.0
pydantic>=2.0.0
aiofiles>=23.0.0
prometheus-client>=0.17.0
EOF

# Create docker-compose.yml
cat > docker-compose.yml <<EOF
version: '3.8'

services:
  jetson-ai-server:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - /tmp/model_swap:/tmp/model_swap
      - ./logs:/app/logs
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    runtime: nvidia
    restart: unless-stopped
    
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
EOF

echo ""
echo "✅ Enhanced Jetson AI Server Setup Complete!"
echo "=============================================="
echo ""
echo "🚀 Quick Start:"
echo "  1. Start server:     ./start_server.sh"
echo "  2. Test server:      python test_server.py"
echo "  3. Monitor system:   python monitor_system.py"
echo ""
echo "🌐 API Documentation: http://localhost:8000/docs"
echo "📊 System Status:     http://localhost:8000/status"
echo ""
echo "🔧 System Service:"
echo "  Enable:  sudo systemctl enable jetson-ai-server"
echo "  Start:   sudo systemctl start jetson-ai-server"
echo "  Status:  sudo systemctl status jetson-ai-server"
echo ""
echo "🐳 Docker Alternative:"
echo "  Build:   docker-compose build"
echo "  Run:     docker-compose up -d"
echo ""
echo "📁 Important Files:"
echo "  - enhanced_model_server.py  (Core AI server)"
echo "  - performance_optimizer.py  (Optimization engine)"
echo "  - api_server.py            (REST API server)"
echo "  - configs/server_config.json (Configuration)"
echo ""
echo "🎉 Your enhanced multi-model AI server is ready!"
EOF

chmod +x setup_enhanced_system.sh
