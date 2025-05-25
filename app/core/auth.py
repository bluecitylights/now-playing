from fastapi import Request, Depends
from app.core.spotify import (
    get_spotify_client, SpotifyApi
)
from app.core.session import store_user_session, clear_user_session, update_token_in_session, get_user_from_session
import time


def get_callback_url(spotify_client: SpotifyApi) -> str:
    return spotify_client.get_auth_url()


async def handle_callback(request: Request, code: str, spotify_client: SpotifyApi) -> None:
    tokens = await spotify_client.exchange_code_for_token(code)
    access_token = tokens["access_token"]

    user_data = await spotify_client.get_user(access_token)

    store_user_session(request, user_data, tokens)


def logout_user(request: Request):
    clear_user_session(request)

async def refresh_access_token(request: Request) -> str:
    user = get_user_from_session(request)
    refresh_token = user["refresh_token"]
    tokens = await refresh_access_token(refresh_token)
    update_token_in_session(request.session, tokens)

    return tokens["access_token"]

async def get_valid_access_token(request: Request) -> str:
    user = get_user_from_session(request)

    token_expiry = user.get("token_expiry", 0)
    if time.time() > token_expiry - 60:
        await refresh_access_token(request.session)
        user = request.session.get("user")

    return user["access_token"]