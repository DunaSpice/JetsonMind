"""Enhanced FastAPI server with PostgreSQL integration"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Conversations, Messages, Users
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(title="Phase 3 Chat API", version="1.0.0")

@app.get("/conversations")
async def get_conversations(db: Session = Depends(get_db)):
    """Get all conversations from existing chat history"""
    conversations = db.query(Conversations).all()
    return conversations

@app.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, db: Session = Depends(get_db)):
    """Get messages for a specific conversation"""
    messages = db.query(Messages).filter(Messages.conversation_id == conversation_id).all()
    return messages

@app.post("/conversations/{conversation_id}/messages")
async def add_message(
    conversation_id: str, 
    content: str, 
    role: str = "user",
    db: Session = Depends(get_db)
):
    """Add new message to existing conversation"""
    message = Messages(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        content=content,
        role=role,
        created_at=datetime.utcnow()
    )
    db.add(message)
    db.commit()
    return message

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
