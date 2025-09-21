#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import gc

app = FastAPI(title="Simple AI Test Server")

# Global model storage
models = {}

class InferenceRequest(BaseModel):
    prompt: str
    max_length: int = 20

class ModelLoadRequest(BaseModel):
    model_name: str

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/status")
def status():
    return {
        "active_models": list(models.keys()),
        "model_count": len(models),
        "memory_usage_gb": torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0
    }

@app.post("/load_model")
def load_model(request: ModelLoadRequest):
    try:
        print(f"Loading model: {request.model_name}")
        
        tokenizer = AutoTokenizer.from_pretrained(request.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        model = AutoModelForCausalLM.from_pretrained(request.model_name)
        
        models[request.model_name] = {
            "model": model,
            "tokenizer": tokenizer,
            "load_time": time.time()
        }
        
        return {"message": f"Model {request.model_name} loaded successfully"}
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/inference")
def inference(request: InferenceRequest):
    try:
        # Use first available model
        if not models:
            return {"error": "No models loaded"}
        
        model_name = list(models.keys())[0]
        model_data = models[model_name]
        
        model = model_data["model"]
        tokenizer = model_data["tokenizer"]
        
        # Tokenize input
        inputs = tokenizer.encode(request.prompt, return_tensors="pt")
        
        # Generate
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + request.max_length,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.eos_token_id
            )
        
        inference_time = time.time() - start_time
        
        # Decode result
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        tokens_generated = len(outputs[0]) - len(inputs[0])
        
        return {
            "response": result,
            "model_used": model_name,
            "inference_time": inference_time,
            "tokens_generated": tokens_generated,
            "tokens_per_second": tokens_generated / inference_time if inference_time > 0 else 0
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
