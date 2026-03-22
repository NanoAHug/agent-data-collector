from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.conversation import ConversationResponse, ConversationList, Stats
from app.services.conversation import ConversationService
from app.core.security import verify_web_session

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=ConversationList)
def list_conversations(
    skip: int = 0,
    limit: int = 50,
    session_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_web_session)
):
    service = ConversationService(db)
    return service.get_list(skip, limit, session_id, date_from, date_to)


@router.get("/{id}", response_model=ConversationResponse)
def get_conversation(
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_web_session)
):
    service = ConversationService(db)
    conversation = service.get_by_id(id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return service._to_response(conversation)


@router.delete("/{id}")
def delete_conversation(
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_web_session)
):
    service = ConversationService(db)
    if not service.delete(id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "success"}
