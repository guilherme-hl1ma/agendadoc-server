import base64
from fastapi import Response
from sqlmodel import Session, select
from starlette.middleware.base import BaseHTTPMiddleware

from src.models import User
from src.database import engine


class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        whitelist_paths = ["/signup", "/docs", "/openapi.json", "/redoc"]
        path = request.url.path
        if path in whitelist_paths:
            return await call_next(request)

        auth = request.headers.get("Authorization")

        if not auth:
            return Response(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="Login Required"'},
            )

        _, b64_credentials = auth.split(" ", 1)
        byte_credentials = base64.b64decode(b64_credentials)
        decoded_credentials = byte_credentials.decode("utf-8")
        email, password = decoded_credentials.split(":")

        with Session(engine) as session:
            user = session.exec(
                select(User).where(User.email == email, User.password == password)
            ).first()
            if not user:
                return Response(
                    status_code=401,
                    headers={"WWW-Authenticate": 'Basic realm="Login Required"'},
                )
        return await call_next(request)
