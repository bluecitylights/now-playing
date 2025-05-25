import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.core.session import get_user_from_session
from app.core.templates import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_user_from_session(request)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})