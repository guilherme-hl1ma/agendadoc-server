from typing import Union
from dotenv import load_dotenv

from fastapi import FastAPI
from pydantic import BaseModel
from sqlmodel import select
from src.database import SessionDep
from src.middleware import BasicAuthMiddleware
from src.models import User

load_dotenv()

app = FastAPI()

app.add_middleware(BasicAuthMiddleware)


class UserAuth(BaseModel):
    email: str
    password: str


@app.post("/signup")
def signup(user: User, session: SessionDep):
    session.add(user)


@app.get("/users")
async def get_users(session: SessionDep):
    return session.exec(select(User)).all()
