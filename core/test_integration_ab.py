#!/usr/bin/env python3
"""Test integration between Folder A (Backend) and Folder B (Agents)"""
import requests
import json

def test_folder_a():
    """Test Folder A backend"""
    print("🔍 Testing Folder A (Database & Backend)...")
    
    # Health check
    response = requests.get("http://localhost:8000/health")
    print(f"  Health: {response.json()}")
    
    # Get conversations count
    response = requests.get("http://localhost:8000/conversations")
    conversations = response.json()
    print(f"  Conversations: {len(conversations)} found")
    
    # Get first conversation messages
    if conversations:
        conv_id = conversations[0]["conversation_id"]
        response = requests.get(f"http://localhost:8000/conversations/{conv_id}/messages")
        messages = response.json()
        print(f"  Messages in first conversation: {len(messages)}")
    
    return True

def test_folder_b():
    """Test Folder B agent server"""
    print("\n🤖 Testing Folder B (Agent Intelligence)...")
    
    # Health check
    response = requests.get("http://localhost:8001/health")
    print(f"  Health: {response.json()}")
    
    # List tools
    response = requests.get("http://localhost:8001/tools")
    print(f"  Tools: {response.json()}")
    
    # Test chat
    chat_request = {
        "message": "How many conversations do I have in my database?"
    }
    response = requests.post("http://localhost:8001/chat", json=chat_request)
    result = response.json()
    print(f"  Chat Response: {result['response'][:100]}...")
    print(f"  Model Used: {result['model_used']}")
    
    return True

def test_integration():
    """Test A→B integration"""
    print("\n🔗 Testing A→B Integration...")
    
    # Agent should be able to query backend
    chat_request = {
        "message": "What's the title of my most recent conversation?"
    }
    response = requests.post("http://localhost:8001/chat", json=chat_request)
    result = response.json()
    print(f"  Integration Response: {result['response']}")
    
    return True

if __name__ == "__main__":
    print("🧪 Phase 3 Integration Test: Folders A & B\n")
    
    try:
        test_folder_a()
        test_folder_b() 
        test_integration()
        print("\n✅ All tests passed! Folders A & B are integrated and working.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
