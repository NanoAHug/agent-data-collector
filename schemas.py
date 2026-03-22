"""
Pydantic数据模型
"""
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class ConversationCreate(BaseModel):
    session_id: str
    timestamp: str
    user_input: str
    assistant_response: str
    context_messages: List[Dict] = []
    metadata: Dict = {}


class ConversationResponse(BaseModel):
    id: int
    session_id: str
    timestamp: str
    user_input: str
    assistant_response: str
    context_messages: List[Dict]
    metadata: Dict
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    total: int
    items: List[ConversationResponse]


class Stats(BaseModel):
    total_conversations: int
    today_conversations: int
    unique_sessions: int
