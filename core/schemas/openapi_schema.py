#!/usr/bin/env python3
"""
Phase 3: OpenAPI Schema Definition
Comprehensive API specification for model management and inference
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from enum import Enum

class ModelTier(str, Enum):
    ram = "ram"
    swap = "swap"
    storage = "storage"

class TaskCapability(str, Enum):
    text_generation = "text-generation"
    text_classification = "text-classification"
    chat = "chat"
    code_generation = "code-generation"
    embeddings = "embeddings"

class Priority(str, Enum):
    speed = "speed"
    quality = "quality"
    balanced = "balanced"

# Request Models
class ModelSelectionRequest(BaseModel):
    model: Optional[str] = Field(None, description="Specific model name")
    auto_select: Optional[bool] = Field(None, description="Enable automatic selection")
    priority: Optional[Priority] = Field("balanced", description="Selection priority")
    capabilities: Optional[List[TaskCapability]] = Field(["text-generation"], description="Required capabilities")

class HotLoadRequest(BaseModel):
    model_name: str = Field(..., description="Name for the new model")
    model_config: Dict[str, Any] = Field(..., description="Model configuration")

class TierMoveRequest(BaseModel):
    model_name: str = Field(..., description="Model to move")
    target_tier: ModelTier = Field(..., description="Target storage tier")

class LimitsUpdateRequest(BaseModel):
    ram_max_gb: Optional[float] = Field(None, ge=1.0, le=16.0, description="Maximum RAM allocation")
    swap_max_gb: Optional[float] = Field(None, ge=2.0, le=32.0, description="Maximum swap allocation")
    ram_reserved_gb: Optional[float] = Field(None, ge=0.5, le=4.0, description="Reserved RAM for system")

class InferenceRequest(BaseModel):
    prompt: str = Field(..., description="Input text prompt")
    model: Optional[str] = Field(None, description="Specific model to use")
    max_tokens: Optional[int] = Field(100, ge=1, le=2048, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(0.9, ge=0.0, le=1.0, description="Top-p sampling")
    stream: Optional[bool] = Field(False, description="Enable streaming response")

# Response Models
class ModelInfo(BaseModel):
    name: str
    size_gb: float
    tier: ModelTier
    capabilities: List[TaskCapability]
    load_time_estimate: float

class ModelSelectionResponse(BaseModel):
    status: str
    model: Optional[str] = None
    size_gb: Optional[float] = None
    tier: Optional[ModelTier] = None
    capabilities: Optional[List[TaskCapability]] = None
    selection_reason: Optional[str] = None
    selection_time_ms: Optional[float] = None
    swap_executed: Optional[bool] = None
    swap_time: Optional[float] = None
    performance_target_met: Optional[bool] = None
    reason: Optional[str] = None

class HotLoadResponse(BaseModel):
    status: str
    job_id: Optional[str] = None
    model_name: Optional[str] = None
    estimated_time: Optional[str] = None
    reason: Optional[str] = None

class JobStatusResponse(BaseModel):
    job_id: str
    model_name: str
    status: str
    progress: float
    elapsed_time: float
    error: Optional[str] = None

class TierStatusResponse(BaseModel):
    status: str
    tiers: Dict[str, Dict[str, Union[float, int]]]

class TierMoveResponse(BaseModel):
    status: str
    job_id: Optional[str] = None
    model_name: Optional[str] = None
    operation: Optional[str] = None
    source_tier: Optional[str] = None
    target_tier: Optional[str] = None
    reason: Optional[str] = None

class InferenceResponse(BaseModel):
    status: str
    model_used: Optional[str] = None
    generated_text: Optional[str] = None
    tokens_generated: Optional[int] = None
    inference_time_ms: Optional[float] = None
    reason: Optional[str] = None

class StreamingChunk(BaseModel):
    chunk_id: int
    text: str
    is_final: bool
    tokens_so_far: int

# System Status Models
class SystemMetrics(BaseModel):
    ram_available_gb: float
    total_available_gb: float
    current_model: Optional[str]
    models_loaded: int
    avg_selection_time_ms: float

class ModelLibraryResponse(BaseModel):
    status: str
    models: Dict[str, ModelInfo]
    total_models: int
    active_hot_loads: int

# Error Models
class ErrorResponse(BaseModel):
    status: str = "error"
    reason: str
    error_code: Optional[str] = None
    available_models: Optional[List[str]] = None

# OpenAPI Schema Generation
def generate_openapi_schema() -> Dict:
    """Generate complete OpenAPI 3.0 schema"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Phase 3 Model Management & Inference API",
            "version": "3.0.0",
            "description": "Advanced model management with dynamic optimization and inference capabilities",
            "contact": {
                "name": "Model Management System",
                "url": "https://github.com/your-repo/model-management"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Local development server"
            }
        ],
        "paths": {
            "/models/select": {
                "post": {
                    "summary": "Select and load a model",
                    "description": "Select a model using manual, automatic, or intelligent selection",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ModelSelectionRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Model selection successful",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ModelSelectionResponse"}
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid request",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/models/hot-load": {
                "post": {
                    "summary": "Hot load a new model",
                    "description": "Add a new model to the system while it's running",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HotLoadRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Hot loading started",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HotLoadResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/models/list": {
                "get": {
                    "summary": "List all available models",
                    "description": "Get information about all models in the system",
                    "responses": {
                        "200": {
                            "description": "Model list retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ModelLibraryResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/tiers/status": {
                "get": {
                    "summary": "Get tier status",
                    "description": "Get current memory tier utilization",
                    "responses": {
                        "200": {
                            "description": "Tier status retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TierStatusResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/tiers/move": {
                "post": {
                    "summary": "Move model between tiers",
                    "description": "Move a model between RAM and swap tiers",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TierMoveRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Tier move started",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TierMoveResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/inference/generate": {
                "post": {
                    "summary": "Generate text",
                    "description": "Generate text using the selected model",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/InferenceRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Text generated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/InferenceResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/inference/stream": {
                "post": {
                    "summary": "Stream text generation",
                    "description": "Generate text with streaming response",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/InferenceRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Streaming response",
                            "content": {
                                "text/event-stream": {
                                    "schema": {"$ref": "#/components/schemas/StreamingChunk"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "ModelSelectionRequest": ModelSelectionRequest.model_json_schema(),
                "HotLoadRequest": HotLoadRequest.model_json_schema(),
                "TierMoveRequest": TierMoveRequest.model_json_schema(),
                "LimitsUpdateRequest": LimitsUpdateRequest.model_json_schema(),
                "InferenceRequest": InferenceRequest.model_json_schema(),
                "ModelSelectionResponse": ModelSelectionResponse.model_json_schema(),
                "HotLoadResponse": HotLoadResponse.model_json_schema(),
                "TierStatusResponse": TierStatusResponse.model_json_schema(),
                "TierMoveResponse": TierMoveResponse.model_json_schema(),
                "InferenceResponse": InferenceResponse.model_json_schema(),
                "StreamingChunk": StreamingChunk.model_json_schema(),
                "ErrorResponse": ErrorResponse.model_json_schema(),
                "ModelLibraryResponse": ModelLibraryResponse.model_json_schema()
            }
        }
    }

if __name__ == "__main__":
    import json
    schema = generate_openapi_schema()
    print(json.dumps(schema, indent=2))
