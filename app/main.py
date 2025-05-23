import secrets
from fastapi import FastAPI, Request, HTTPException, Header, Response, Cookie, Query
from fastapi.responses import RedirectResponse
import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
STATE_COOKIE_NAME = "spotify_auth_state"

@app.get("/login")
def login():
    state = secrets.token_urlsafe(16)
    scopes = "user-read-currently-playing user-read-playback-state"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": scopes,
        "state": state,
    }
    url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    response = RedirectResponse(url)
    response.set_cookie(key="spotify_auth_state", value=state, httponly=True)
    return response

@app.get("/callback")
def callback(
    code: str = Query(...),
    state: str = Query(...),
    request: Request = None
):
    stored_state = request.cookies.get("spotify_auth_state")
    if state != stored_state:
        raise HTTPException(status_code=400, detail="State mismatch or missing")

    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=payload, headers=headers)

    if response.status_code != 200:
        return {"error": "Failed to get token", "details": response.json()}

    tokens = response.json()
    return {
        "access_token": tokens["access_token"],
        "expires_in": tokens["expires_in"],
        "refresh_token": tokens.get("refresh_token"),
    }

@app.get("/currently-playing")
def currently_playing(authorization: str = Header(...)):
    headers = {"Authorization": f"Bearer {authorization}"}
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Spotify API error")
    data = response.json()
    return {
        "track": data["item"]["name"],
        "artist": data["item"]["artists"][0]["name"],
        "album": data["item"]["album"]["name"]
    }