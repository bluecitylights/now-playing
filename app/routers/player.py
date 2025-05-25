from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.core.spotify import (
    spotify_play,
    spotify_pause,
    spotify_next,
    spotify_previous
)
from app.core.templates import templates
from app.core.auth import get_valid_access_token

router = APIRouter()

@router.post("/player/play", response_class=HTMLResponse)
async def player_play(request: Request):
    access_token = await get_valid_access_token(request)
    success = await spotify_play(access_token)
    if success:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Playing"})
    else:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Paused"})

@router.post("/player/pause", response_class=HTMLResponse)
async def player_pause(request: Request):
    access_token = await get_valid_access_token(request)
    success = await spotify_pause(access_token)
    if success:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Paused"})
    else:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Playing"})

@router.post("/player/next", response_class=HTMLResponse)
async def player_next(request: Request):
    access_token = await get_valid_access_token(request)
    success = await spotify_next(access_token)
    if success:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Skipped to next track"})
    else:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "FAiled to skip to next track"})

@router.post("/player/previous", response_class=HTMLResponse)
async def player_previous(request: Request):
    access_token = await get_valid_access_token(request)
    success = await spotify_previous(access_token)
    if success:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "Skipped to previous track"})
    else:
        return templates.TemplateResponse("partials/playback_status.html", {"request": request, "status": "FAiled to skip to previous track"})