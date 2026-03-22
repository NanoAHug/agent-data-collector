import json
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models import Conversation
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationList,
    Stats
)


class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ConversationCreate) -> Conversation:
        conversation = Conversation(
            session_id=data.session_id,
            timestamp=data.timestamp,
            user_input=data.user_input,
            assistant_response=data.assistant_response,
            context_messages=json.dumps(data.context_messages, ensure_ascii=False),
            meta_data=json.dumps(data.metadata, ensure_ascii=False)
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_id(self, id: int) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(Conversation.id == id).first()

    def get_list(
        self,
        skip: int = 0,
        limit: int = 50,
        session_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> ConversationList:
        query = self.db.query(Conversation)
        
        if session_id:
            query = query.filter(Conversation.session_id == session_id)
        
        if date_from:
            query = query.filter(Conversation.created_at >= date_from)
        
        if date_to:
            query = query.filter(Conversation.created_at <= date_to + " 23:59:59")
        
        total = query.count()
        items = query.order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()
        
        return ConversationList(
            total=total,
            items=[self._to_response(item) for item in items]
        )

    def delete(self, id: int) -> bool:
        conversation = self.get_by_id(id)
        if not conversation:
            return False
        self.db.delete(conversation)
        self.db.commit()
        return True

    def get_stats(self) -> Stats:
        total = self.db.query(Conversation).count()
        
        today = date.today()
        today_count = self.db.query(Conversation).filter(
            func.date(Conversation.created_at) == today
        ).count()
        
        unique_sessions = self.db.query(Conversation.session_id).distinct().count()
        
        return Stats(
            total_conversations=total,
            today_conversations=today_count,
            unique_sessions=unique_sessions
        )

    def _to_response(self, conversation: Conversation) -> ConversationResponse:
        return ConversationResponse(
            id=conversation.id,
            session_id=conversation.session_id,
            timestamp=conversation.timestamp,
            user_input=conversation.user_input,
            assistant_response=conversation.assistant_response,
            context_messages=json.loads(conversation.context_messages) if conversation.context_messages else [],
            metadata=json.loads(conversation.meta_data) if conversation.meta_data else {},
            created_at=conversation.created_at
        )
