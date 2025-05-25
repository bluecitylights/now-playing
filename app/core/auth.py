from fastapi import Request
from app.core.spotify import (
    get_spotify_auth_url,
    exchange_code_for_token,
    get_spotify_user,
    refresh_access_token,
)
from app.core.session import store_user_session, clear_user_session, update_token_in_session, get_user_from_session
import time


def get_callback_url() -> str:
    return get_spotify_auth_url()


async def handle_callback(request: Request, code: str) -> None:
    tokens = await exchange_code_for_token(code)
    access_token = tokens["access_token"]

    user_data = await get_spotify_user(access_token)

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