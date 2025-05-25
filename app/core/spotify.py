import os, httpx
from urllib.parse import urlencode
import logging
from typing import Dict, Any, Optional

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_SCOPES = "user-read-currently-playing user-read-playback-state user-modify-playback-state"
SPOTIFY_BASE_URL = "https://api.spotify.com/v1"
SPOTIFY_ME_URL = f"{SPOTIFY_BASE_URL}/me"
SPOTIFY_PLAYER_URL = f"{SPOTIFY_ME_URL}/player"


SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class SpotifyApi:
        def __init__(self, client_id: str, client_secret: str, redicrect_uri: str):
            self.client_id = client_id
            self.client_secret = client_secret
            self.redirect_uri = redicrect_uri
            self.scopes = SPOTIFY_SCOPES
            self.auth_url = SPOTIFY_AUTH_URL
            self.token_url = SPOTIFY_TOKEN_URL
            self.base_api_url = SPOTIFY_BASE_URL
            self.me_url = f"{self.base_api_url}/me"
            self.player_url = f"{self.me_url}/player"

        def get_auth_url(self):
            params = {
                "client_id": self.client_id,
                "response_type": "code",
                "redirect_uri": self.redirect_uri,
                "scope": self.scopes,
                "show_dialog": "true"
            }
            return f"{self.auth_url}?{urlencode(params)}"
        
        async def _make_api_request(self,
                                method: str,
                                url: str,
                                access_token: Optional[str] = None,
                                data: Optional[Dict[str, Any]] = None,
                                headers: Optional[Dict[str, str]] = None,
                                content_type: str = "application/json") -> httpx.Response:
            
            req_headers = {"Content-Type": content_type}
            if access_token:
                req_headers["Authorization"] = f"Bearer {access_token}"
            if headers:
                req_headers.update(headers)

            async with httpx.AsyncClient() as client:
                try:
                    if method == "GET":
                        response = await client.get(url, headers=req_headers)
                    elif method == "POST":
                        response = await client.post(url, headers=req_headers, data=data)
                    elif method == "PUT":
                        # For PUT requests, Spotify often expects a JSON body, not form-urlencoded
                        response = await client.put(url, headers=req_headers, json=data)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                    response.raise_for_status() # Raise for 4xx/5xx status codes
                    return response
                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP error for {url}: {e.response.status_code} - {e.response.text}")
                    raise
                except httpx.RequestError as e:
                    logger.error(f"Network error for {url}: {e}")
                    raise
                except Exception as e:
                    logger.error(f"An unexpected error occurred during API request to {url}: {e}")
                    raise
        async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            response = await self._make_api_request(
                "POST",
                self.token_url,
                data=data,
                content_type="application/x-www-form-urlencoded"
            )
            return response.json()

        async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            response = await self._make_api_request(
                "POST",
                self.token_url,
                data=data,
                content_type="application/x-www-form-urlencoded"
            )
            return response.json()

        async def get_user(self, access_token: str) -> Dict[str, Any]:
            response = await self._make_api_request("GET", self.me_url, access_token=access_token)
            return response.json()

        async def get_current_playback(self, access_token: str) -> Optional[Dict[str, Any]]:
            url = f"{self.player_url}/currently-playing"
            try:
                response = await self._make_api_request("GET", url, access_token=access_token)
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 204: # No content, nothing is playing
                    return None
                raise # Re-raise other HTTP errors

        async def play(self, access_token: str, device_id: Optional[str] = None) -> bool:
            url = f"{self.player_url}/play"
            data = {"device_ids": [device_id]} if device_id else None # Spotify expects device_ids as a list
            try:
                response = await self._make_api_request("PUT", url, access_token=access_token, data=data)
                # Spotify returns 204 No Content for successful playback control
                return response.status_code in (204, 202, 200)
            except httpx.HTTPStatusError as e:
                logger.error(f"Failed to play Spotify: {e.response.status_code} - {e.response.text}")
                return False
            except Exception as e:
                logger.error(f"An unexpected error occurred during Spotify play: {e}")
                return False

        async def pause(self, access_token: str) -> bool:
            url = f"{self.player_url}/pause"
            try:
                response = await self._make_api_request("PUT", url, access_token=access_token)
                return response.status_code in (204, 202, 200)
            except httpx.HTTPStatusError as e:
                logger.error(f"Failed to pause Spotify: {e.response.status_code} - {e.response.text}")
                return False
            except Exception as e:
                logger.error(f"An unexpected error occurred during Spotify pause: {e}")
                return False

        async def next(self, access_token: str) -> bool:
            url = f"{self.player_url}/next"
            try:
                # Spotify API for next/previous uses POST, but without a body
                response = await self._make_api_request("POST", url, access_token=access_token)
                return response.status_code in (204, 202, 200)
            except httpx.HTTPStatusError as e:
                logger.error(f"Failed to skip to next track: {e.response.status_code} - {e.response.text}")
                return False
            except Exception as e:
                logger.error(f"An unexpected error occurred during Spotify next track: {e}")
                return False

        async def previous(self, access_token: str) -> bool:
            url = f"{self.player_url}/previous"
            try:
                # Spotify API for next/previous uses POST, but without a body
                response = await self._make_api_request("POST", url, access_token=access_token)
                return response.status_code in (204, 202, 200)
            except httpx.HTTPStatusError as e:
                logger.error(f"Failed to skip to previous track: {e.response.status_code} - {e.response.text}")
                return False
            except Exception as e:
                logger.error(f"An unexpected error occurred during Spotify previous track: {e}")
                return False
        


            

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
    
_spotify_client_instance: Optional[SpotifyApi] = None

def set_spotify_client_instance(client: SpotifyApi):
    global _spotify_client_instance
    _spotify_client_instance = client

def get_spotify_client() -> SpotifyApi:
    if _spotify_client_instance is None:
        # This should ideally not happen if set_spotify_client_instance is called correctly
        # during app startup. If it does, it indicates a setup issue.
        raise RuntimeError("SpotifyAPIClient has not been initialized. "
                           "Ensure set_spotify_client_instance is called during app startup.")
    return _spotify_client_instance