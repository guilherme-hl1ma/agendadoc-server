from uuid import uuid4
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import redis
from sqlmodel import select

from src.database import SessionDep
from src.models import User
from src.security.encrypt_password import hash_password, verify_password


redis_instance = redis.Redis(host="localhost", port=6379, decode_responses=True)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup_basic")
def signup_basic_auth(user: User, session: SessionDep):
    try:
        user_db = session.exec(select(User).where(User.email == user.email)).first()
        if user_db:
            raise HTTPException(
                status_code=409,
                detail="E-mail already exists. Try again using another one.",
            )

        password = user.password
        hashed = hash_password(password)
        user.password = hashed

        session.add(user)
        session.commit()
        session.refresh(user)
    except HTTPException as e:
        raise e

    return JSONResponse(status_code=201, content={"detail": "User registered."})


@router.post("/signup")
def signup_session(user: User, session: SessionDep, request: Request):
    try:
        user_db = session.exec(select(User).where(User.email == user.email)).first()
        if user_db:
            raise HTTPException(
                status_code=409,
                detail="E-mail already exists. Try again using another one.",
            )

        email = user.email
        password = user.password
        hashed = hash_password(password)
        user.password = hashed

        session_id = uuid4()
        response = JSONResponse(status_code=201, content={"detail": "User registered."})
        response.set_cookie(
            key="ses_num",
            value=str(session_id),
            httponly=True,
            # secure=True,
            samesite="lax",
            max_age=60 * 60 * 24,
        )
        redis_instance.set(
            name=f"session_id:{session_id}", value=email, ex=60 * 60 * 24
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return response
    except HTTPException as e:
        raise e


@router.post("/login")
def signin_session(user: User, session: SessionDep, request: Request):
    try:
        email = user.email
        password = user.password

        user_db = session.exec(select(User).where(User.email == email)).first()

        is_pass_correct = verify_password(
            plain_password=password, hashed_password=user_db.password
        )

        if not user_db or not is_pass_correct:
            raise HTTPException(
                status_code=404,
                detail="Invalid user. Try again.",
            )

        session_id = uuid4()
        response = JSONResponse(status_code=200, content={"detail": "OK"})
        response.set_cookie(
            key="ses_num",
            value=str(session_id),
            httponly=True,
            # secure=True,
            samesite="lax",
            max_age=60 * 60 * 24,
        )
        redis_instance.set(
            name=f"session_id:{session_id}", value=email, ex=60 * 60 * 24
        )

        return response
    except HTTPException as e:
        raise e


@router.post("/logout")
def signout_session(request: Request):
    session_id = request.cookies.get("ses_num")
    print("Session: ", session_id)

    response = JSONResponse(status_code=200, content={"detail": "OK"})

    if session_id:
        redis_instance.delete(f"session_id:{session_id}")
        response.delete_cookie("ses_num")

    return response
