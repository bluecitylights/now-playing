import os
import time
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from app.core.auth import get_valid_access_token
import httpx

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/now-playing", response_class=HTMLResponse)
async def now_playing(request: Request):
    try:
        access_token = await get_valid_access_token(request)
    except Exception:
        return RedirectResponse("/")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.spotify.com/v1/me/player/currently-playing",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if resp.status_code == 204:
            return HTMLResponse("<h2>No track is currently playing</h2>")
        resp.raise_for_status()
        data = resp.json()

    album_info = {
        "track": data["item"]["name"],
        "artist": data["item"]["artists"][0]["name"],
        "album": data["item"]["album"]["name"],
        "image": data["item"]["album"]["images"][0]["url"]
    }

    return templates.TemplateResponse("now_playing.html", {"request": request, "album": album_info})
