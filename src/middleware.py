from pydantic import BaseModel
from main import app


class BasicAuthHeader(BaseModel):
    email: str
    password: str


@app.middleware("http")
async def basic_auth():
    pass
