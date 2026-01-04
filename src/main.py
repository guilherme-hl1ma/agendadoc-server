import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from src.middleware import BasicAuthMiddleware, SessionBasedAuthMiddleware
from .routers import authentication, users


app = FastAPI()

auth_mode = os.getenv("AUTH_MODE")

if auth_mode == "basic":
    app.add_middleware(BasicAuthMiddleware)
elif auth_mode == "session":
    app.add_middleware(SessionBasedAuthMiddleware)

app.include_router(authentication.router)
app.include_router(users.router)
