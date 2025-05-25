import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.routers.pages import router as pages_router
from app.routers.auth import router as auth_router
from app.routers.now_playing import router as now_playing_router

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "some-secret"))

app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(now_playing_router)