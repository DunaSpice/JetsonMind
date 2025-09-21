"""PostgreSQL integration with existing openai_chat_export database"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

# Use same connection as MCP server
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/openai_chat_export"
engine = create_engine(DATABASE_URL)

# Verify connection and data
with engine.connect() as conn:
    conv_count = conn.execute(text("SELECT COUNT(*) FROM conversations")).scalar()
    msg_count = conn.execute(text("SELECT COUNT(*) FROM messages")).scalar()
    print(f"✅ Connected to existing database: {conv_count} conversations, {msg_count} messages")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Auto-map existing tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Access existing tables
Conversations = Base.classes.conversations
Messages = Base.classes.messages
Users = Base.classes.users
MessageFeedback = Base.classes.message_feedback
SharedConversations = Base.classes.shared_conversations

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
