from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.conversation import ConversationCreate
from app.services.conversation import ConversationService
from app.core.security import verify_api_key

router = APIRouter(tags=["collect"])


@router.post("/collect")
def collect_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    service = ConversationService(db)
    conversation = service.create(data)
    return {"status": "success", "id": conversation.id}
