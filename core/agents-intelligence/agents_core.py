"""OpenAI Agents SDK integration with existing inference engine and MCP tools"""
import asyncio
from openai import OpenAI
from typing import Dict, Any, List
import requests
import json

class Phase3Agent:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.backend_url = "http://localhost:8000"
        
    async def process_message(self, message: str, conversation_id: str = None) -> str:
        """Process user message with agent intelligence"""
        
        # Get conversation context if ID provided
        context = []
        if conversation_id:
            context = self._get_conversation_context(conversation_id)
        
        # Use inference engine for model selection
        selected_model = self._select_best_model(message)
        
        # Generate response
        if self.client:
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant with access to conversation history."},
                    *context,
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content
        else:
            return f"[Mock Response] Processed '{message}' with model {selected_model}"
    
    def _get_conversation_context(self, conversation_id: str) -> List[Dict]:
        """Get recent messages from conversation for context"""
        try:
            response = requests.get(f"{self.backend_url}/conversations/{conversation_id}/messages")
            if response.status_code == 200:
                messages = response.json()
                # Return last 5 messages as context
                return [{"role": msg.get("role", "user"), "content": msg.get("content", "")} 
                       for msg in messages[-5:]]
        except:
            pass
        return []
    
    def _select_best_model(self, message: str) -> str:
        """Use existing inference engine for model selection"""
        try:
            from inference_engine import EnhancedModelSelector
            selector = EnhancedModelSelector()
            return selector.select_model(message)
        except:
            return "gpt-4"  # fallback

# MCP Tool Functions
def query_database(query: str) -> str:
    """Query conversation database via API"""
    try:
        response = requests.get(f"http://localhost:8000/conversations")
        return f"Database query result: {len(response.json())} conversations found"
    except:
        return "Database query failed"

def search_conversations(search_term: str) -> str:
    """Search conversations for specific terms"""
    # This would integrate with existing MCP postgres server
    return f"Searching conversations for: {search_term}"

# Agent Tools Registry
AGENT_TOOLS = {
    "query_database": query_database,
    "search_conversations": search_conversations
}
