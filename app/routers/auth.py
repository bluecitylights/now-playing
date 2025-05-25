import os
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.core.auth import handle_callback, get_callback_url, logout_user
from app.core.templates import templates

router = APIRouter()

@router.get("/login")
async def login():
    url = get_callback_url()
    return RedirectResponse(url)

@router.get("/logout")
async def logout(request: Request):
    logout_user(request)
    return RedirectResponse("/")

@router.get("/callback")
async def callback(request: Request, code: str = None, error: str = None):
    await handle_callback(request, code)
    return RedirectResponse("/now-playing")

