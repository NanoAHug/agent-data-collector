from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.security import (
    verify_web_session,
    verify_password,
    create_session,
    remove_session,
    SESSION_COOKIE_NAME
)

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, password: str = Query(...)):
    if not verify_password(password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    token = create_session()
    
    response = HTMLResponse(content='<script>window.location.href="/";</script>')
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=86400
    )
    return response


@router.post("/logout")
async def logout(request: Request):
    remove_session(request)
    
    response = HTMLResponse(content='<script>window.location.href="/login";</script>')
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


@router.get("/", response_class=HTMLResponse)
async def web_ui(request: Request, _: bool = Depends(verify_web_session)):
    return templates.TemplateResponse("index.html", {"request": request})
