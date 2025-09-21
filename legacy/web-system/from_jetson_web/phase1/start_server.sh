#!/bin/bash
cd "."
source venv/bin/activate

echo "🚀 Starting Enhanced Jetson AI Server..."
echo "📊 System Info:"
echo "  RAM: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "  Swap: $(free -h | grep Swap | awk '{print $3 "/" $2}')"
echo "  GPU: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{print $1 "MB/" $2 "MB"}')"
echo "  Temp: $(cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000 "°C"}')"
echo ""

python api_server.py --host 0.0.0.0 --port 8000
