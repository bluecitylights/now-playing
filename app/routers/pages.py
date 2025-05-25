from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    if user:
        return HTMLResponse(f"""
            <h1>Welcome {user['display_name']}!</h1>
            <p><a href="/now-playing">See Now Playing</a></p>
            <p><a href="/logout">Logout</a></p>
        """)
    else:
        return HTMLResponse("""
            <h1>Welcome! Please <a href="/login">login with Spotify</a></h1>
        """)