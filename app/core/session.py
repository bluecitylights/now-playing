import time
from fastapi import Request

def store_user_session(request: Request, user_data: dict, tokens: dict):
    request.session["user"] = {
        "id": user_data["id"],
        "display_name": user_data.get("display_name", "User"),
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "token_expiry": time.time() + tokens.get("expires_in", 3600),
    }

def clear_user_session(request: Request):
    request.session.clear()

def get_user_from_session(request: Request):
    return request.session.get("user")

def update_token_in_session(session, new_tokens: dict):
    session["user"]["access_token"] = new_tokens["access_token"]
    session["user"]["token_expiry"] = time.time() + new_tokens.get("expires_in", 3600)
    if "refresh_token" in new_tokens:
        session["user"]["refresh_token"] = new_tokens["refresh_token"]