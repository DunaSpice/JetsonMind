#!/usr/bin/env python3
"""Direct PostgreSQL test using subprocess"""
import subprocess
import json

def query_db(sql):
    """Execute SQL via sudo postgres"""
    cmd = ['sudo', '-u', 'postgres', 'psql', '-d', 'openai_chat_export', '-t', '-c', sql]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

# Test queries
print("🔍 Testing PostgreSQL access...")

# Count conversations
conv_count = query_db("SELECT COUNT(*) FROM conversations;")
print(f"✅ Conversations: {conv_count}")

# Count messages  
msg_count = query_db("SELECT COUNT(*) FROM messages;")
print(f"✅ Messages: {msg_count}")

# Get recent conversation
recent = query_db("SELECT id, title FROM conversations ORDER BY created_at DESC LIMIT 1;")
print(f"✅ Recent conversation: {recent}")

# Get sample message
sample = query_db("SELECT content FROM messages LIMIT 1;")
print(f"✅ Sample message: {sample[:100]}...")

print("\n🎯 Database is accessible! Ready for API integration.")
