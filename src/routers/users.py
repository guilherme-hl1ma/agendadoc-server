from fastapi import APIRouter, HTTPException
from sqlmodel import select

from src.database import SessionDep
from src.models import User


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_users(session: SessionDep):
    try:
        return session.exec(select(User)).all()
    except HTTPException as e:
        raise e
