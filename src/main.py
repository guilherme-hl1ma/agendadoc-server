from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from src.middleware import BasicAuthMiddleware
from .routers import authentication, users


app = FastAPI()

app.add_middleware(BasicAuthMiddleware)
app.include_router(authentication.router)
app.include_router(users.router)
