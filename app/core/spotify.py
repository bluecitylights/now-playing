import os, httpx
from urllib.parse import urlencode
import logging

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_SCOPES = "user-read-currently-playing user-read-playback-state user-modify-playback-state"
SPOTIFY_BASE_URL = "https://api.spotify.com/v1"
SPOTIFY_ME_URL = f"{SPOTIFY_BASE_URL}/me"
SPOTIFY_PLAYER_URL = f"{SPOTIFY_ME_URL}/player"

def get_spotify_auth_url():
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPES,
        "show_dialog": "true"
    }
    return f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"

async def exchange_code_for_token(code: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
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
        response.raise_for_status()
        return response.json()

async def get_spotify_user(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            SPOTIFY_ME_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()
    
async def refresh_access_token(refresh_token: str) -> dict:
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
        return response.json()
    
async def get_current_playback(access_token: str) -> dict | None:
    url = f"{SPOTIFY_PLAYER_URL}/currently-playing"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 204:  # No content, nothing is playing
            return None
        
        response.raise_for_status()
        return response.json()
    
async def spotify_play(access_token: str) -> bool:
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{SPOTIFY_PLAYER_URL}/play", headers=headers)
        if response.status_code in (204, 202, 200):
            return True
        logging.error(f"spotify_play failed: {response.status_code} {response.text}")
        return False

async def spotify_pause(access_token: str) -> bool:
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    async with httpx.AsyncClient() as client:
        print('pause!!')
        print(f"{SPOTIFY_PLAYER_URL}/pause")
        response = await client.put(f"{SPOTIFY_PLAYER_URL}/pause", headers=headers)
        if response.status_code in (204, 202, 200):
            return True
        logging.error(f"spotify_pause failed: {response.status_code} {response.text}")
        return False

async def spotify_next(access_token: str) -> bool:
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{SPOTIFY_PLAYER_URL}/next", headers=headers)
        if response.status_code in (204, 202, 200):
            return True
        logging.error(f"spotify_next failed: {response.status_code} {response.text}")
        return False

async def spotify_previous(access_token: str) -> bool:
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{SPOTIFY_PLAYER_URL}/previous", headers=headers)
        if response.status_code in (204, 202, 200):
            return True
        logging.error(f"spotify_previous failed: {response.status_code} {response.text}")
        return False