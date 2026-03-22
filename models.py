"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    timestamp = Column(String)
    user_input = Column(Text)
    assistant_response = Column(Text)
    context_messages = Column(Text)
    meta_data = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
