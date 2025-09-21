# Async Preparation Plan - All Phases

## 🚀 **PARALLEL PREPARATION STRATEGY**

### Pre-create all test scripts, directories, and monitoring tools simultaneously

---

## 📁 **DIRECTORY STRUCTURE SETUP**

```bash
# Create all phase directories at once
mkdir -p from_jetson_web/test_results/{phase3_small,phase4_medium,phase5_large,phase6_vlm,phase7_phi}
mkdir -p from_jetson_web/test_results/scripts
mkdir -p from_jetson_web/test_results/monitoring
```

---

## 📝 **PHASE 3: SMALL LLM SCRIPTS**

### Models: Qwen 2.5 (0.5B, 1.5B), Llama 3.2 1B
```python
# phase3_test_script.py
models_phase3 = [
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct", 
    "meta-llama/Llama-3.2-1B-Instruct"
]
```

---

## 📝 **PHASE 4: MEDIUM LLM SCRIPTS**

### Models: SmolLM2 1.7B, Qwen 3B, Llama 3B, Gemma 2B
```python
# phase4_test_script.py
models_phase4 = [
    "HuggingFaceTB/SmolLM2-1.7B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "google/gemma-2-2b-it"
]
```

---

## 📝 **PHASE 5: LARGE LLM SCRIPTS**

### Models: Qwen 7B, Llama 8B
```python
# phase5_test_script.py
models_phase5 = [
    "Qwen/Qwen2.5-7B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct"
]
```

---

## 📝 **PHASE 6: VLM SCRIPTS**

### Models: LLaVA, Qwen VL, Phi Vision, Gemma Vision
```python
# phase6_vlm_script.py
models_phase6 = [
    "llava-hf/llava-1.5-7b-hf",
    "Qwen/Qwen2.5-VL-3B-Instruct",
    "Qwen/Qwen2.5-VL-7B-Instruct",
    "microsoft/Phi-3.5-vision-instruct"
]
```

---

## 📝 **PHASE 7: PHI SCRIPTS**

### Models: Phi 3 Mini, Phi 3.5 Mini
```python
# phase7_phi_script.py
models_phase7 = [
    "microsoft/Phi-3-mini-4k-instruct",
    "microsoft/Phi-3.5-mini-instruct"
]
```

---

## 🔧 **UNIVERSAL TEST TEMPLATE**

```python
# universal_test_template.py
import torch
import time
import psutil
import json
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_model(model_name, phase, test_prompt="Hello, how are you?"):
    results = {
        "model": model_name,
        "phase": phase,
        "status": "unknown",
        "load_time": 0,
        "inference_time": 0,
        "memory_used": 0,
        "output": "",
        "error": ""
    }
    
    start_time = time.time()
    
    try:
        # Memory before
        mem_before = psutil.virtual_memory().used / 1024**3
        
        # Load model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="cuda"
        )
        
        load_time = time.time() - start_time
        
        # Test inference
        inference_start = time.time()
        inputs = tokenizer.encode(test_prompt, return_tensors="pt").to("cuda")
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + 10,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id
            )
        
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        inference_time = time.time() - inference_start
        
        # Memory after
        mem_after = psutil.virtual_memory().used / 1024**3
        
        results.update({
            "status": "success",
            "load_time": load_time,
            "inference_time": inference_time,
            "memory_used": mem_after - mem_before,
            "output": result
        })
        
    except Exception as e:
        results.update({
            "status": "failed",
            "error": str(e)
        })
    
    return results
```

---

## 📊 **MONITORING SETUP**

```python
# system_monitor.py
import psutil
import nvidia_ml_py3 as nvml
import time
import json

def monitor_system():
    nvml.nvmlInit()
    handle = nvml.nvmlDeviceGetHandleByIndex(0)
    
    return {
        "timestamp": time.time(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_available": psutil.virtual_memory().available / 1024**3,
        "gpu_memory_used": nvml.nvmlDeviceGetMemoryInfo(handle).used / 1024**3,
        "gpu_memory_total": nvml.nvmlDeviceGetMemoryInfo(handle).total / 1024**3,
        "gpu_utilization": nvml.nvmlDeviceGetUtilizationRates(handle).gpu
    }
```

---

## 🔄 **BATCH EXECUTION SCRIPT**

```python
# batch_executor.py
import json
import time
from universal_test_template import test_model
from system_monitor import monitor_system

def run_phase(phase_name, model_list, output_file):
    results = []
    
    for model in model_list:
        print(f"Testing {model}...")
        
        # Pre-test monitoring
        pre_stats = monitor_system()
        
        # Run test
        result = test_model(model, phase_name)
        
        # Post-test monitoring
        post_stats = monitor_system()
        
        result["pre_stats"] = pre_stats
        result["post_stats"] = post_stats
        
        results.append(result)
        
        # Save immediately
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ {model}: {result['status']}")
        
        # Cool down between tests
        time.sleep(5)
    
    return results
```

---

## 📋 **EXECUTION COMMANDS**

### All phases prepared simultaneously:

```bash
# Phase 3 - Small Models
docker run --runtime nvidia --rm -v /tmp/jetson_models:/data -v $(pwd)/from_jetson_web/test_results:/results dustynv/mlc:r36.4.0 python3 /results/scripts/phase3_test_script.py

# Phase 4 - Medium Models  
docker run --runtime nvidia --rm -v /tmp/jetson_models:/data -v $(pwd)/from_jetson_web/test_results:/results dustynv/mlc:r36.4.0 python3 /results/scripts/phase4_test_script.py

# Phase 5 - Large Models
docker run --runtime nvidia --rm -v /tmp/jetson_models:/data -v $(pwd)/from_jetson_web/test_results:/results dustynv/mlc:r36.4.0 python3 /results/scripts/phase5_test_script.py

# Phase 6 - VLM Models
docker run --runtime nvidia --rm -v /tmp/jetson_models:/data -v $(pwd)/from_jetson_web/test_results:/results dustynv/mlc:r36.4.0 python3 /results/scripts/phase6_vlm_script.py

# Phase 7 - Phi Models
docker run --runtime nvidia --rm -v /tmp/jetson_models:/data -v $(pwd)/from_jetson_web/test_results:/results dustynv/mlc:r36.4.0 python3 /results/scripts/phase7_phi_script.py
```

---

## ⚡ **ASYNC BENEFITS**

1. **All scripts ready** - No waiting between phases
2. **Consistent testing** - Same template for all models
3. **Real-time monitoring** - System stats for each test
4. **Immediate results** - JSON output after each model
5. **Failure recovery** - Continue testing if one model fails
6. **Resource tracking** - Memory/GPU usage per model

---

## 🎯 **READY FOR PARALLEL EXECUTION**

**Next Step**: Create all scripts and directories, then execute phases sequentially with full async preparation complete.
