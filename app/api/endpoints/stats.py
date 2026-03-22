from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.conversation import Stats
from app.services.conversation import ConversationService
from app.core.security import verify_web_session

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=Stats)
def get_stats(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_web_session)
):
    service = ConversationService(db)
    return service.get_stats()
