from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.core.spotify import (
    get_spotify_client,
    SpotifyApi
)
from app.core.templates import templates
from app.core.auth import get_valid_access_token

router = APIRouter()

@router.post("/player/play", response_class=HTMLResponse)
async def player_play(request: Request, spotify_client: SpotifyApi = Depends(get_spotify_client)):
    access_token = await get_valid_access_token(request)
    success = await spotify_client.play(access_token)
    if success:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Playing"})
    else:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Paused"})

@router.post("/player/pause", response_class=HTMLResponse)
async def player_pause(request: Request, spotify_client: SpotifyApi = Depends(get_spotify_client)):
    access_token = await get_valid_access_token(request)
    success = await spotify_client.pause(access_token)
    if success:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Paused"})
    else:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Playing"})

@router.post("/player/next", response_class=HTMLResponse)
async def player_next(request: Request, spotify_client: SpotifyApi = Depends(get_spotify_client)):
    access_token = await get_valid_access_token(request)
    success = await spotify_client.next(access_token)
    if success:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Skipped to next track"})
    else:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "FAiled to skip to next track"})

@router.post("/player/previous", response_class=HTMLResponse)
async def player_previous(request: Request, spotify_client: SpotifyApi = Depends(get_spotify_client)):
    access_token = await get_valid_access_token(request)
    success = await spotify_client.previous(access_token)
    if success:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Skipped to previous track"})
    else:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "FAiled to skip to previous track"})