# Testing Plan: Remaining Orin Nano Compatible Models

## Based on Jetson AI Lab Models Page - Orin Nano Compatible

---

## 🎯 **PHASE 3: Small Language Models (0.5B-1B)**

### Priority 1 - Smallest Models
1. **Qwen 2.5 0.5B** - `Qwen/Qwen2.5-0.5B-Instruct`
2. **Qwen 2.5 1.5B** - `Qwen/Qwen2.5-1.5B-Instruct`
3. **Llama 3.2 1B** - `meta-llama/Llama-3.2-1B-Instruct`

### Test Commands:
```bash
# Test each model with PyTorch approach
docker run --runtime nvidia --rm dustynv/mlc:r36.4.0 python3 -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
model = AutoModelForCausalLM.from_pretrained('MODEL_NAME', torch_dtype=torch.float16, device_map='cuda')
tokenizer = AutoTokenizer.from_pretrained('MODEL_NAME')
# Test inference
"
```

---

## 🎯 **PHASE 4: Medium Language Models (1.7B-3B)**

### Priority 2 - Medium Models
1. **SmolLM2 1.7B** - `HuggingFaceTB/SmolLM2-1.7B-Instruct`
2. **Qwen 2.5 3B** - `Qwen/Qwen2.5-3B-Instruct`
3. **Llama 3.2 3B** - `meta-llama/Llama-3.2-3B-Instruct`
4. **Gemma 2 2B** - `google/gemma-2-2b-it`

---

## 🎯 **PHASE 5: Larger Language Models (7B-8B)**

### Priority 3 - Large Models (Memory Intensive)
1. **Qwen 2.5 7B** - `Qwen/Qwen2.5-7B-Instruct`
2. **Llama 3.1 8B** - `meta-llama/Llama-3.1-8B-Instruct`

### Special Considerations:
- Monitor memory usage closely
- May require swap usage
- Test with 4-bit quantization if needed

---

## 🎯 **PHASE 6: Vision-Language Models (VLM)**

### Priority 4 - VLM Models
1. **LLaVA 1.5 7B** - `llava-hf/llava-1.5-7b-hf`
2. **Qwen 2.5 VL 3B** - `Qwen/Qwen2.5-VL-3B-Instruct`
3. **Qwen 2.5 VL 7B** - `Qwen/Qwen2.5-VL-7B-Instruct`
4. **Phi 3.5 Vision** - `microsoft/Phi-3.5-vision-instruct`
5. **Gemma 3 1B** - `google/paligemma-3b-pt-224`
6. **Gemma 3 4B** - `google/paligemma-3b-mix-224`

### VLM Test Requirements:
- Image processing capabilities
- Multi-modal input handling
- Vision encoder + language decoder

---

## 🎯 **PHASE 7: Microsoft Phi Models**

### Priority 5 - Phi Models
1. **Phi 3 Mini 4K** - `microsoft/Phi-3-mini-4k-instruct`
2. **Phi 3.5 Mini 128K** - `microsoft/Phi-3.5-mini-instruct`
3. **Phi 4 Multimodal** - `microsoft/Phi-4` (if available)

---

## 📋 **EXECUTION STRATEGY**

### Step-by-Step Approach:
1. **Test one model at a time**
2. **Monitor system resources** (RAM, GPU memory)
3. **Document results immediately**
4. **Save successful configurations**
5. **Note any failures with details**

### Test Template for Each Model:
```python
# Standard test template
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time

model_name = "MODEL_NAME_HERE"
start_time = time.time()

try:
    print(f"Testing {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="cuda"
    )
    
    # Test inference
    text = "Hello, how are you?"
    inputs = tokenizer.encode(text, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[1] + 10,
            do_sample=True,
            temperature=0.7
        )
    
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"✅ SUCCESS: {result}")
    print(f"Time: {time.time() - start_time:.2f}s")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
```

---

## 📊 **SUCCESS CRITERIA**

### For Each Model:
- ✅ **Loads successfully** without OOM errors
- ✅ **Generates coherent text** 
- ✅ **Completes within reasonable time** (<60s for loading)
- ✅ **System remains stable** after test

### Memory Thresholds:
- **Small models (0.5B-1B)**: Should use <2GB GPU memory
- **Medium models (1.7B-3B)**: Should use <4GB GPU memory  
- **Large models (7B-8B)**: May use up to 6GB + swap

---

## 📁 **DOCUMENTATION PLAN**

### Files to Create:
1. `phase3_small_llm_results.md` - 0.5B-1B model results
2. `phase4_medium_llm_results.md` - 1.7B-3B model results
3. `phase5_large_llm_results.md` - 7B-8B model results
4. `phase6_vlm_results.md` - Vision-language model results
5. `phase7_phi_results.md` - Microsoft Phi model results
6. `model_performance_comparison.md` - Speed/memory comparison
7. `working_models_final_list.md` - Complete compatibility list

---

## ⚡ **EXECUTION ORDER**

### Recommended Testing Sequence:
1. **Start with Phase 3** (smallest models first)
2. **Test one model per phase** before moving to next
3. **Document results immediately** after each test
4. **Monitor system health** between tests
5. **Stop if system becomes unstable**

### Time Estimate:
- **Phase 3**: ~30 minutes (3 models)
- **Phase 4**: ~45 minutes (4 models)  
- **Phase 5**: ~30 minutes (2 models, may be slower)
- **Phase 6**: ~60 minutes (6 VLM models, complex)
- **Phase 7**: ~30 minutes (3 Phi models)
- **Total**: ~3 hours for complete testing

---

## 🚀 **READY TO EXECUTE**

**Next Command**: Start with Phase 3, Model 1 (Qwen 2.5 0.5B)

All models listed are confirmed compatible with Orin Nano according to Jetson AI Lab documentation.
