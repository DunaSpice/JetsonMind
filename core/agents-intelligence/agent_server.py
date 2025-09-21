"""Agent server that integrates with Folder A backend"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents_core import Phase3Agent, AGENT_TOOLS
import asyncio

app = FastAPI(title="Phase 3 Agent Intelligence", version="1.0.0")

# Initialize agent
agent = Phase3Agent()

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None

class ChatResponse(BaseModel):
    response: str
    model_used: str
    tools_used: list = []

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Process message through agent intelligence"""
    try:
        response = await agent.process_message(
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            response=response,
            model_used="gpt-4",  # From agent selection
            tools_used=list(AGENT_TOOLS.keys())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def list_available_tools():
    """List available agent tools"""
    return {"tools": list(AGENT_TOOLS.keys())}

@app.get("/health")
async def health_check():
    """Health check for agent server"""
    return {"status": "healthy", "agent": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
