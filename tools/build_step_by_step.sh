#!/bin/bash

echo "=========================================="
echo "STEP 1: Pre-build checks"
echo "=========================================="
echo "Current time: $(date)"
echo "Memory status:"
free -h
echo ""
echo "Checkpoint files:"
ls -la /home/petr/jetson-containers/data/models/tensorrt_llm/CodeLlama-7B-Instruct-GPTQ/
echo ""

echo "=========================================="
echo "STEP 2: Starting Docker container"
echo "=========================================="
cd /home/petr/jetson-containers

echo "=========================================="
echo "STEP 3: Building TensorRT engine"
echo "=========================================="
echo "This will take 5-15 minutes..."
echo "Building with minimal settings for faster completion"
echo ""

./run.sh dustynv/tensorrt_llm:0.12-r36.4.0 bash -c "
echo 'CONTAINER: Starting engine build...'
echo 'CONTAINER: Memory inside container:'
free -h
echo ''

echo 'CONTAINER: Running trtllm-build command...'
trtllm-build \
  --checkpoint_dir /data/models/tensorrt_llm/CodeLlama-7B-Instruct-GPTQ \
  --output_dir /data/models/tensorrt_llm/CodeLlama-7B-Instruct-GPTQ/engines \
  --max_batch_size 1 \
  --max_input_len 128 \
  --max_seq_len 256 \
  --max_beam_width 1

echo ''
echo 'CONTAINER: Build completed, checking results:'
ls -la /data/models/tensorrt_llm/CodeLlama-7B-Instruct-GPTQ/engines/
"

echo ""
echo "=========================================="
echo "STEP 4: Post-build verification"
echo "=========================================="
echo "Final engine files:"
ls -la /home/petr/jetson-containers/data/models/tensorrt_llm/CodeLlama-7B-Instruct-GPTQ/engines/

if [ -f "/home/petr/jetson-containers/data/models/tensorrt_llm/CodeLlama-7B-Instruct-GPTQ/engines/config.json" ]; then
    echo ""
    echo "✅ SUCCESS: Engine build completed!"
    echo "Engine is ready for inference"
else
    echo ""
    echo "❌ FAILED: Engine build did not complete"
    echo "No config.json found in engines directory"
fi

echo ""
echo "=========================================="
echo "BUILD PROCESS COMPLETE"
echo "=========================================="
