"""
FastAPI 对话数据收集服务器
"""
from fastapi import FastAPI, Depends, HTTPException, Request, Query, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
import json
import os
import secrets
from typing import Optional

from database import get_db, init_db
from models import Conversation
from schemas import ConversationCreate, ConversationResponse, ConversationList, Stats

API_KEY = os.environ.get("DATA_COLLECTION_API_KEY")
if not API_KEY:
    raise RuntimeError("DATA_COLLECTION_API_KEY environment variable is not set. Please run 'python generate_token.py' to generate one.")
SESSION_COOKIE_NAME = "auth_token"

app = FastAPI(title="datacollector", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

active_sessions = {}


def verify_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=403, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid Authorization header format. Use: Bearer <token>")
    
    token = authorization[7:]
    if token != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True


def verify_web_session(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token or token not in active_sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@app.on_event("startup")
def startup():
    init_db()


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, password: str = Query(...)):
    if password != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    token = secrets.token_urlsafe(32)
    active_sessions[token] = datetime.now()
    
    response = HTMLResponse(content='<script>window.location.href="/";</script>')
    response.set_cookie(key=SESSION_COOKIE_NAME, value=token, httponly=True, max_age=86400)
    return response


@app.post("/logout")
async def logout(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token and token in active_sessions:
        del active_sessions[token]
    
    response = HTMLResponse(content='<script>window.location.href="/login";</script>')
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


@app.post("/api/collect")
def collect_conversation(
    data: ConversationCreate, 
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    conversation = Conversation(
        session_id=data.session_id,
        timestamp=data.timestamp,
        user_input=data.user_input,
        assistant_response=data.assistant_response,
        context_messages=json.dumps(data.context_messages, ensure_ascii=False),
        meta_data=json.dumps(data.metadata, ensure_ascii=False)
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return {"status": "success", "id": conversation.id}


@app.get("/api/conversations", response_model=ConversationList)
def list_conversations(
    skip: int = 0,
    limit: int = 50,
    session_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_web_session)
):
    query = db.query(Conversation)
    
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
        items=[ConversationResponse(
            id=item.id,
            session_id=item.session_id,
            timestamp=item.timestamp,
            user_input=item.user_input,
            assistant_response=item.assistant_response,
            context_messages=json.loads(item.context_messages) if item.context_messages else [],
            metadata=json.loads(item.meta_data) if item.meta_data else {},
            created_at=item.created_at
        ) for item in items]
    )


@app.get("/api/conversations/{id}", response_model=ConversationResponse)
def get_conversation(
    id: int, 
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_web_session)
):
    conversation = db.query(Conversation).filter(Conversation.id == id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
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


@app.get("/api/stats", response_model=Stats)
def get_stats(
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_web_session)
):
    total = db.query(Conversation).count()
    
    today = date.today()
    today_count = db.query(Conversation).filter(
        func.date(Conversation.created_at) == today
    ).count()
    
    unique_sessions = db.query(Conversation.session_id).distinct().count()
    
    return Stats(
        total_conversations=total,
        today_conversations=today_count,
        unique_sessions=unique_sessions
    )


@app.delete("/api/conversations/{id}")
def delete_conversation(
    id: int, 
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_web_session)
):
    conversation = db.query(Conversation).filter(Conversation.id == id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    return {"status": "success"}


@app.get("/", response_class=HTMLResponse)
async def web_ui(request: Request, authorized: bool = Depends(verify_web_session)):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
