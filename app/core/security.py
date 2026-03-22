import secrets
from datetime import datetime
from typing import Dict

from fastapi import HTTPException, Header, Request

from app.config import get_settings

settings = get_settings()

SESSION_COOKIE_NAME = "auth_token"
active_sessions: Dict[str, datetime] = {}


def verify_api_key(authorization: str = Header(None)) -> bool:
    if not authorization:
        raise HTTPException(status_code=403, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=403, 
            detail="Invalid Authorization header format. Use: Bearer <token>"
        )
    
    token = authorization[7:]
    if not secrets.compare_digest(token, settings.api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True


def verify_web_session(request: Request) -> bool:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token or token not in active_sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


def create_session() -> str:
    token = secrets.token_urlsafe(32)
    active_sessions[token] = datetime.now()
    return token


def remove_session(request: Request) -> None:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token and token in active_sessions:
        del active_sessions[token]


def verify_password(password: str) -> bool:
    return secrets.compare_digest(password, settings.api_key)
