import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from app.core.auth import handle_callback, get_callback_url, logout_user
from app.core.spotify import SpotifyApi, get_spotify_client

router = APIRouter()

@router.get("/login")
async def login(spotify_client: SpotifyApi = Depends(get_spotify_client)):
    url = get_callback_url(spotify_client)
    return RedirectResponse(url)

@router.get("/logout")
async def logout(request: Request):
    logout_user(request)
    return RedirectResponse("/")

@router.get("/callback")
async def callback(request: Request, code: str = None, error: str = None, spotify_client: SpotifyApi = Depends(get_spotify_client)):
    await handle_callback(request, code, spotify_client)
    return RedirectResponse("/now-playing")

