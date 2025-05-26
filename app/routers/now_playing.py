from http.client import HTTPException
import os
import time
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.core.auth import get_valid_access_token
import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.core.auth import get_valid_access_token
from app.core.spotify import get_current_playback
from app.core.session import get_user_from_session
from app.core.templates import templates
from app.core.spotify import SpotifyApi, get_spotify_client

router = APIRouter()

@router.get("/now-playing")
async def now_playing(request: Request, spotify_client: SpotifyApi = Depends(get_spotify_client)):
    user = get_user_from_session(request)
    access_token = await get_valid_access_token(request)
    playback = await spotify_client.get_current_playback(access_token)
    track = playback["item"]
    return templates.TemplateResponse(
        "now_playing.html",
        {
            "request": request,
            "user": user,
            "track": track,
            "playback": playback
        }
    )

@router.get("/now-playing/progress")
async def now_playing_progress(request: Request, spotify_client: SpotifyApi = Depends(get_spotify_client)):
    access_token = await get_valid_access_token(request)
    playback = await spotify_client.get_current_playback(access_token)

    if not playback or not playback.get("item"):
        return JSONResponse(content={"track_id": None, "progress_ms": 0, "duration_ms": 0})

    track = playback["item"]
    return JSONResponse(
        content={
            "track_id": track["id"],
            "progress_ms": playback.get("progress_ms", 0),
            "duration_ms": track.get("duration_ms", 0)
        }
    )


@router.get("/now-playing/track-info", response_class=HTMLResponse)
async def now_playing_track_info(request: Request, spotify_client: SpotifyApi = Depends(get_spotify_client)):
    access_token = await get_valid_access_token(request)
    playback = await spotify_client.get_current_playback(access_token)

    if not playback or not playback.get("item"):
        return HTMLResponse(content="<p>No track playing</p>")

    track = playback["item"]
    from fastapi.templating import Jinja2Templates
    return templates.TemplateResponse(
        "partials/track_info.html",
        {
            "request": request, 
            "track": track
        }
    )
