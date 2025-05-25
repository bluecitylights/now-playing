import secrets
from fastapi import FastAPI, Request, HTTPException, Header, Response, Cookie, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import requests
from dotenv import load_dotenv
import httpx
import time
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
import httpx
from urllib.parse import urlencode

load_dotenv()
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "some-random-secret"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SCOPES = "user-read-currently-playing user-read-playback-state"


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    if user:
        return HTMLResponse(f"""
            <h1>Welcome {user['display_name']}!</h1>
            <p><a href="/logout">Logout</a></p>
        """)
    else:
        return HTMLResponse("""
            <h1>Welcome! Please <a href="/login">login with Spotify</a></h1>
        """)

@app.get("/login")
async def login():
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPES,
        "show_dialog": "true"
    }
    url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)

async def refresh_access_token(session):
    refresh_token = session["user"].get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token available")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": SPOTIFY_CLIENT_ID,
                "client_secret": SPOTIFY_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        tokens = response.json()

        # Update session with new token info
        session["user"]["access_token"] = tokens["access_token"]
        expires_in = tokens.get("expires_in", 3600)
        session["user"]["token_expiry"] = time.time() + expires_in
        # Refresh token may or may not be returned; only update if present
        if "refresh_token" in tokens:
            session["user"]["refresh_token"] = tokens["refresh_token"]

        return tokens["access_token"]
    
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")



@app.get("/now-playing", response_class=HTMLResponse)
async def now_playing(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/")  # or raise HTTPException(401)

    # Refresh token if expired
    token_expiry = user.get("token_expiry", 0)
    if time.time() > token_expiry - 60:
        access_token = await refresh_access_token(request.session)
    else:
        access_token = user["access_token"]

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


@app.get("/callback")
async def callback(request: Request, code: str = None, error: str = None):
    if error:
        return HTMLResponse(f"Error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            SPOTIFY_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": SPOTIFY_REDIRECT_URI,
                "client_id": SPOTIFY_CLIENT_ID,
                "client_secret": SPOTIFY_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_response.raise_for_status()
        tokens = token_response.json()

        access_token = tokens["access_token"]
        expires_in = tokens.get("expires_in", 3600)
        refresh_token = tokens.get("refresh_token")

        user_response = await client.get(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_response.raise_for_status()
        user_data = user_response.json()

    request.session["user"] = {
        "id": user_data["id"],
        "display_name": user_data.get("display_name", "User"),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_expiry": time.time() + expires_in,
    }

    return RedirectResponse("/now-playing")