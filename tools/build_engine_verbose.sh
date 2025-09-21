#!/bin/bash

# TensorRT-LLM Engine Build with Progress Monitoring
set -e

CHECKPOINT_DIR="/data/models/tensorrt_llm/CodeLlama-7B-Instruct-GPTQ"
ENGINE_DIR="/data/models/tensorrt_llm/CodeLlama-7B-Instruct-GPTQ/engines"
LOG_FILE="/tmp/tensorrt_build.log"

echo "=== TensorRT-LLM Engine Build Started ==="
echo "Timestamp: $(date)"
echo "Checkpoint: $CHECKPOINT_DIR"
echo "Output: $ENGINE_DIR"
echo "Log file: $LOG_FILE"
echo "Memory: $(free -h | grep Mem:)"
echo "Swap: $(free -h | grep Swap:)"
echo "=========================================="

# Start build with verbose logging
cd /home/petr/jetson-containers

./run.sh dustynv/tensorrt_llm:0.12-r36.4.0 bash -c "
  set -x
  echo '=== Container Environment ==='
  nvidia-smi || echo 'nvidia-smi failed'
  free -h
  df -h /data
  
  echo '=== Starting TensorRT Build ==='
  export CUDA_LAUNCH_BLOCKING=1
  export NCCL_DEBUG=INFO
  export TENSORRT_VERBOSE=1
  
  trtllm-build \
    --checkpoint_dir $CHECKPOINT_DIR \
    --output_dir $ENGINE_DIR \
    --max_batch_size 1 \
    --max_input_len 512 \
    --max_seq_len 1024 \
    --max_beam_width 1 \
    --gemm_plugin float16 \
    --gpt_attention_plugin float16 \
    --context_fmha enable \
    --paged_kv_cache enable \
    --remove_input_padding enable 2>&1 | tee $LOG_FILE
  
  echo '=== Build Results ==='
  ls -la $ENGINE_DIR/
  echo '=== Memory After Build ==='
  free -h
" 2>&1 | while IFS= read -r line; do
  echo "[$(date '+%H:%M:%S')] $line"
done

echo "=== Build Complete ==="
echo "Final engine files:"
ls -la /home/petr/jetson-containers/data/models/tensorrt_llm/CodeLlama-7B-Instruct-GPTQ/engines/
echo "Log saved to: $LOG_FILE"
